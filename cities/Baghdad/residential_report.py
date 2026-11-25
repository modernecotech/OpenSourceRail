"""Render the selected housing-to-centre study and its matching delivery estimate."""


def refresh_headline(path, study):
    selected = study["delivery"][study["selection"]]
    quantities, workforce = (selected["construction"][key] for key in ("quantities", "workforce"))
    costs = selected["systems"]["cost_cases"]
    low, base, high = (costs[key]["installed_planning_usd_m"] / 1000 for key in ("low", "base", "high"))
    text = (
        f"**Current housing-to-centre budget case.** {quantities['unique_guideway_km']:,.1f} km of mapped guideway, "
        f"{quantities['double_track_km']:,.1f} track-km counting both running tracks, and {quantities['station_sites']:,} station sites. "
        f"The base installed allowance is **US${base:.2f}bn**, with planning cases of US${low:.2f}bn to US${high:.2f}bn. "
        f"Casting, haul and erection account for {workforce['paid_deck_and_casting_hours']/1e6:.2f} million paid hours. "
        "The six-minute operating offer and the construction schedule use this same candidate. "
        "[Quantities, labour and costs](NETWORK-DELIVERY.md) · [Housing journeys and map](NETWORK.md)"
    )
    content = path.read_text()
    start = "<!-- current housing budget -->"
    end = "<!-- end current housing budget -->"
    prefix, remainder = content.split(start)
    _, suffix = remainder.split(end)
    return (prefix + start + "\n\n" + text + "\n\n" + end + suffix).encode()


def _pct(number):
    return f"{number:.2f}%"


def _minutes(time):
    return "—" if time is None else f"{time:.1f}"


def _terminal_names(action, stations):
    return " → ".join(stations.get(code, {}).get("name", code) for code in action["new_terminal_ids"])


def corridor_sections(study, stations):
    audit = study["corridor_consolidation"]
    before, after = audit["before_totals"], audit["after_totals"]
    settings = audit["before"]["settings"]
    out = ["## Removing overlapping suburban routes", "",
           "The earlier alignment shortlist measured proximity against the network used to generate it. "
           "Later additions could run alongside lines chosen in the meantime. G05 and G09, for example, "
           "left the same M02 terminus on the same mapped approach.", "",
           f"The new screen compares every pair of lines in the assembled map. It measures runs of at least "
           f"{settings['min_run_m']/1000:g} km, within {settings['nearby_m']/1000:g} km and "
           f"{settings['max_angle_deg']:g}° of parallel in either direction. It counts approaches departing the same "
           f"terminal cluster within {settings['terminal_m']/1000:g} km and reports alignments within "
           f"{settings['common_m']:g} m separately. Pair-km count each line pair, so three lines can count the same "
           "corridor more than once. The walking model tests changes independently using streets and station entrances in the planning data.", "",
           "| Geometry check | Previous housing map | Revised map |", "|---|---:|---:|",
           f"| Close parallel corridor pairs, km | {before['nearby_parallel_m']/1000:.2f} | {after['nearby_parallel_m']/1000:.2f} |",
           f"| Near-identical alignment pairs, km | {before['common_alignment_m']/1000:.2f} | {after['common_alignment_m']/1000:.2f} |",
           f"| Line pairs leaving nearby termini in parallel | {before['terminal_fans']} | {after['terminal_fans']} |", "",
           "The consolidation compares the same six-minute service and housing trips with the previous map. "
           "A change must reduce the measured duplication, retain a connected passenger graph and stay within the declared limits "
           "for walking access, transfers, each destination, travel time and load concentration.", "",
           "| Edited line | Revised extent | Route km removed | Reason |", "|---|---|---:|---|"]
    for action in audit["actions"]:
        out.append(f"| {action['line_id']} | {_terminal_names(action, stations) or 'Withdrawn service'} | "
                   f"{action['removed_route_km']:.2f} | {action['reason']} |")
    if audit["after"]["runs"]:
        out.extend(["", "The longest remaining alignments flagged for review are shown below. The machine record includes "
                    "locations, all variants tested and any access penalties that stopped a proposed cut.", "",
                    "| Remaining pair | Approximate parallel length | Median separation |", "|---|---:|---:|"])
        for row in audit["after"]["runs"][:5]:
            out.append(f"| {' / '.join(row['lines'])} | {row['length_m']/1000:.2f} km | {row['median_distance_m']:,.0f} m |")
        first_trials = audit["passes"][0]["trials"] if audit["passes"] else {}
        why = first_trials.get("g04-at-m04", {}).get("access")
        if why and why["served_loss_pp"] > study["policy"]["corridor_selection"]["served_loss_pp"]:
            out.extend(["", f"For example, turning G04 back at M04 reduced its parallel section with M01, but took away "
                        f"two-change access on {why['served_loss_pp']:.2f} percentage points of all weighted journeys. "
                        f"At the worst affected centre the loss was {why['destination_loss_pp']:.2f} points. The revised layout keeps that section."])
    out.extend(["", "The geometry screen identifies where to test sharing, shortening or rerouting. "
                "Separate catchments, turnbacks, track junctions and service capacity need explicit evidence before construction.", ""])
    return out


def pathway_sections(study, stations):
    cases = study["candidates"]
    selected = study["selection"]
    comparison = study["common_service"]
    sample = comparison["demand_sample"]
    variants = comparison["variants"]
    outcome = variants[selected]
    baseline = study["corridor_consolidation"]["before_layout"]
    centres = {row["id"]: row for row in study["destinations"]}
    out = ["## Housing-to-centre journeys", "",
           f"The model tests {sample['origin_count']:,} populated housing tiles against {sample['destination_count']} named central destinations. "
           "WorldPop residential population represents origins outside the selected central box. Each destination has equal weight in this trial. "
           "Both walks follow mapped streets and must be within 1.2 km. Rail paths allow zero, one or two changes. "
           "A constrained search still finds a valid two-change route when a faster route would take three changes.", "",
           f"**Selected layout — {cases[selected]['name']}**. Every test uses the same six-minute directional service offer. "
           "First choose the shortest perimeter layout that stays within the trial’s access and journey-time bands. Then test central links "
           "on that layout and retain the best gain in two-change reach if one-change reach holds and the network remains shorter than the earlier grid. "
           "The consolidation then checks those journeys again after removing parallel sections.", "",
           "| Layout | Route km removed | Direct available | Within one change | Within two changes | P90 elapsed (min) | Access screen |",
           "|---|---:|---:|---:|---:|---:|---|"]
    for code, option in cases.items():
        trip = variants[code]["journeys"]
        available = trip["reachable_with_at_most_share_of_all_pct"]
        name = f"**{option['name']}**" if code == selected else option["name"]
        status = "Within bands" if option["equivalent_access_screen"] else ", ".join(
            key.replace("_pp", "").replace("_min", "").replace("_", " ") for key in option["exceeded"])
        out.append(f"| {name} | {option['removed_route_km']:.2f} | {_pct(available['0'])} | {_pct(available['1'])} | "
                   f"{_pct(available['2'])} | {_minutes(trip['elapsed_p90_min'])} | {status} |")
    trip = outcome["journeys"]
    link = study["access_link_tests"]
    if link["selected_line"]:
        out.extend(["", f"The access stage assigned journeys on {len(link['evaluated'])} compatible additional links. "
                    f"It retained **{link['selected_line']}** for the improvement in trips to the named centres. "
                    "The machine record holds the results and reasons for rejected alignments."])
    out.extend(["", f"In the selected layout, **{_pct(trip['outside_walking_limit_share_pct'])}** of weighted pairs miss the walking limit at one or both ends. "
                f"Another **{_pct(trip['eligible_but_unserved_share_pct'])}** have eligible walks but lack a rail path within two changes. "
                "The assignment chooses the fastest generalised journey among those admitted. Its transfer mix can differ from availability by transfer limit.", "",
                "| Destination | Previous housing map within two changes | Revised map within two changes | Revised P90 (min) |",
                "|---|---:|---:|---:|"])
    for code, place in centres.items():
        before = variants[baseline]["destinations"][code]
        after = outcome["destinations"][code]
        out.append(f"| {place['name']} | {_pct(before['served_share_pct'])} | {_pct(after['served_share_pct'])} | {_minutes(after['elapsed_p90_min'])} |")
    matched = study["equal_train_km"][selected]
    out.extend(["", f"At the previous housing map’s daily train-km, the selected layout could use a provisional "
                f"{matched['service']['directional_headway_s']/60:.2f}-minute interval in each direction. "
                f"The two-change reach is {_pct(matched['journeys']['served_share_pct'])}; the served P90 elapsed time is "
                f"{_minutes(matched['journeys']['elapsed_p90_min'])} minutes. The estimate below prices the common six-minute offer.", "",
                "### Example paths", "",
                "| Changes | Housing tile | Destination | Rail legs | Elapsed (min) |",
                "|---:|---|---|---|---:|"])
    for number, row in outcome["pathway_witnesses"].items():
        parts = [f"{leg['line']} {stations[leg['board_station']]['name']} → {stations[leg['alight_station']]['name']}"
                 for leg in row["rail_legs"]]
        out.append(f"| {number} | {row['origin_id']} | {centres[row['destination_id']]['name']} | "
                   f"{' / '.join(parts)} | {_minutes(row['elapsed_min'])} |")
    out.extend(["", "### Perimeter changes retained from the housing study", "",
                "| Line | Revised extent | Route km removed | Reason |",
                "|---|---|---:|---|"])
    for action in cases[selected]["actions"]:
        termini = _terminal_names(action, stations)
        out.append(f"| {action['line_id']} | {termini or 'Withdrawn service'} | {action['removed_route_km']:.2f} | {action['reason']} |")
    affected = cases[selected]["housing_access"].get("1200", {}).get("estimated_residents_losing_walk_access", 0.)
    out.extend(["", f"Compared with the original grid, an estimated {affected:,.0f} residents lose their 1.2 km walk to rail. "
                "The machine record identifies the largest affected cells and every withdrawn station call. "
                "Land access, turning facilities and local housing demand need the next planning review.", "",
                "### Applying the method in another city", "",
                "The pathway solver accepts a station and line graph, directed street distances, explicit weighted housing origins and central destinations. "
                "Keep those inputs fixed while comparing network edits. Supply each city’s own metric street projection, geometry validator, centre weights and service case. "
                "The [Baghdad input file](residential-access.toml) records the present choices. "
                "[Reusable pathway function](holistic_pathways.py)", ""])
    return out


def delivery_summary(study):
    name, previous = study["selection"], study["corridor_consolidation"]["before_layout"]
    before, after = [study["delivery"][key] for key in (previous, name)]
    q0, q1 = (side["construction"]["quantities"] for side in (before, after))
    p0, p1 = (side["construction"]["programme"] for side in (before, after))
    w0, w1 = (side["construction"]["workforce"] for side in (before, after))
    s0, s1 = (side["systems"]["service"] for side in (before, after))
    b0, b1 = (side["systems"]["cost_cases"]["base"] for side in (before, after))
    return ["## Quantities and delivery on the revised map", "",
            "The previous housing map and revised network below use the same rates, train service and construction resources. "
            "The separate 148 km and 605 km cost studies retain their original scope.", "",
            "| Measure | Previous housing map | Revised layout |", "|---|---:|---:|",
            f"| Passenger service route-km | {q0['service_route_km']:,.2f} | {q1['service_route_km']:,.2f} |",
            f"| Unique mapped guideway km | {q0['unique_guideway_km']:,.2f} | {q1['unique_guideway_km']:,.2f} |",
            f"| Permanent double-track km, both tracks counted | {q0['double_track_km']:,.2f} | {q1['double_track_km']:,.2f} |",
            f"| Passenger station sites / transfers | {q0['station_sites']:,} / {q0['transfer_sites']:,} | {q1['station_sites']:,} / {q1['transfer_sites']:,} |",
            f"| Standard girders / support locations | {q0['standard_girders']:,} / {q0['standard_support_positions']:,} | {q1['standard_girders']:,} / {q1['standard_support_positions']:,} |",
            f"| Casting, haul and erection paid hours | {w0['paid_deck_and_casting_hours']:,.0f} | {w1['paid_deck_and_casting_hours']:,.0f} |",
            f"| Standard-deck handover, relative day | {p0['last_standard_deck_day']:,.0f} | {p1['last_standard_deck_day']:,.0f} |",
            f"| Trainsets, including reserve | {s0['fleet_trainsets']:,} | {s1['fleet_trainsets']:,} |",
            f"| Base installed planning allowance, $bn | {b0['installed_planning_usd_m']/1000:.2f} | {b1['installed_planning_usd_m']/1000:.2f} |",
            f"| Annual operating allowance, $bn | {b0['annual_operations_total_usd_m']/1000:.2f} | {b1['annual_operations_total_usd_m']/1000:.2f} |", "",
            "The deck schedule covers standard deck handover. Station, special structures, system installation and commissioning still need an integrated opening programme. "
            "[Construction work orders, labour and full estimate](NETWORK-DELIVERY.md)", ""]


def _route_table(construction):
    out = ["## Construction packages", "",
           "| Line | Passenger route km | Allocated guideway km | Girders | Supports | Method | Calendar days | Paid casting and erection hours | Base deck cost, $m |",
           "|---|---:|---:|---:|---:|---|---:|---:|---:|"]
    register = {row["line"]: row for row in construction["quantities"]["route_register"]}
    for row in construction["orders"]:
        fields = register[row["section"]]
        cost = row.get("civil_scope_usd", {}).get("base", 0.)
        calendar = "—" if row["calendar_days"] is None else f"{row['calendar_days']:,.0f}"
        out.append(f"| {row['section']} | {fields['service_route_km']:.2f} | {fields['unique_guideway_km']:.2f} | "
                   f"{row.get('standard_girders', 0):,} | {row.get('standard_support_positions', 0):,} | "
                   f"{row['selected_planning_method']} | {calendar} | "
                   f"{row.get('paid_total_method_and_casting_hours', 0):,.0f} | {cost/1e6:,.2f} |")
    return out


def delivery_report(record):
    study = record["walking_access"]["through_route_selection"]["residential"]
    item = study["delivery"][study["selection"]]
    civil, system = item["construction"], item["systems"]
    quantities, programme, labour = civil["quantities"], civil["programme"], civil["workforce"]
    service, power, costs = system["service"], system["power"], system["cost_cases"]
    out = ["# Baghdad housing network delivery and cost", "",
           f"Candidate `{civil['candidate_id']}` · [Current network and access analysis](NETWORK.md)", "", *delivery_summary(study),
           "## Resources and calendar", "",
           f"The standard-deck programme uses {programme['active_launcher_pairs']} pairs of opposed launching gantries and "
           f"{programme['active_road_day_teams']} road teams. It needs {programme['concurrent_construction_flatbeds']} simultaneous "
           f"construction flatbeds and up to {programme['concurrent_yard_sites']} concurrently staffed yards "
           f"with {programme['concurrent_moulds']} moulds and {programme['concurrent_yard_area_ha']:.1f} hectares of hardstand and yard area. "
           "Open routes use deck-fed construction where assumed. The road teams and shared yards cover the isolated packages.", "",
           f"The permanent railway uses {quantities['double_track_km']:,.2f} track-km. The construction method also carries "
           f"{quantities['temporary_track_km']:,.2f} km of temporary feed track, which is recovered. It models "
           f"{quantities['loaded_beam_trips']:,} loaded public-road beam trips and {quantities['erection_lane_hours']:,.0f} erection lane-hours. "
           f"{quantities['residual_bays_pending_design']:,} residual bays still need design.", "",
           programme["basis"], "", *_route_table(civil), "", "## Paid construction work by shift", "",
           "| Job group | Role | Shift | Paid hours |", "|---|---|---|---:|"]
    for row in labour["crew_shifts"]:
        out.append(f"| {row['phase']} | {row['role']} | {row['shift']} | {row['paid_hours']:,.0f} |")
    other = labour["additional_standard_support_and_track_planning_hours"]["base"]
    out.extend(["", f"The base productivity assumptions add {other['standard_support_paid_person_hours_at_75pct']:,.0f} paid support hours and "
                f"{other['permanent_track_paid_person_hours']:,.0f} permanent-track hours. The station and system-work crew tables remain open. "
                "The estimate carries their work as installed unit allowances.", "", "## Service and installed budget", "",
                f"The common {service['directional_headway_s']/60:g}-minute, {service['operating_hours_day']:g}-hour offer gives "
                f"{service['running_train_km_day']:,.0f} running train-km/day. The fleet allowance covers {service['active_trainsets']:,} active "
                f"and {service['reserve_trainsets']:,} spare six-car sets, {service['depot_allowances']} depot allowances and "
                f"{service['control_centre_allowances']} control centres. The traction allowance covers {power['nominal_supply_sites']} grid sites "
                f"and approximately {power['annual_grid_gwh']:,.1f} GWh/year. Site ratings and depot movements require simulation.", "",
                "| Direct package, constant 2026 $m | Low | Base | High |", "|---|---:|---:|---:|"])
    cases = ("low", "base", "high")
    for key in costs["base"]["direct_scope_usd_m"]:
        values = " | ".join(f"{costs[case]['direct_scope_usd_m'][key]:,.1f}" for case in cases)
        out.append(f"| {key.replace('_', ' ').capitalize()} | {values} |")
    for label, key in (("Design and assurance", "design_usd_m"), ("Testing and commissioning", "testing_usd_m"),
                       ("Project allowance", "allowance_usd_m"), ("Installed planning total", "installed_planning_usd_m"),
                       ("Annual service and maintenance", "annual_operations_total_usd_m"),
                       (f"{system['years']}-year present cost at service start", "whole_life_present_usd_m")):
        out.append(f"| {label} | " + " | ".join(f"{costs[case][key]:,.1f}" for case in cases) + " |")
    out.extend(["", "Low, base and high are planning sensitivities. Whole-life cost includes operations and the dated renewal allowances in the "
                f"[machine record](baghdad-network.json), discounted at {100*system['discount_rate']:.1f}% real. "
                "The construction spend profile, financing and opening date require a coordinated works programme.", "",
                civil["cost_scope"], "", "## Open work before adopting a programme", ""])
    out.extend(f"- {line}" for line in (*civil["holds"], *system["open_scopes"]))
    out.extend(["", f"Publication `{record['publication_id']}`.", ""])
    return "\n".join(out)
