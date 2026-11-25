"""Construction quantities and unit-price allowances for a Baghdad passenger map."""

from collections import defaultdict
from hashlib import sha256
from itertools import pairwise
from math import ceil, fsum, hypot, isclose
from pathlib import Path

import numpy as np

from cities.Baghdad import holistic_network, iraq_power
from cities.Baghdad.engineering.mechanical.civil import family_comparison, network_delivery
from cities.Baghdad.engineering.mechanical.civil import rail_fed_erection as erection
from cities.Baghdad.engineering.simulation import vehicle_audit
from engineering.design_search import line_benchmark_civil


CITY = Path(__file__).resolve().parent
ROOT = CITY.parents[1]
CASES = network_delivery.CASES
WATER_CONTEXT = holistic_network.INPUTS[-1]


def _length_register(lines):
    """Count an identical mapped edge only once, irrespective of direction."""
    metres_per_degree = holistic_network.LOCAL_METRES
    owners = {}
    overlaps = defaultdict(float)
    route_lengths = {}
    owned_lengths = {}
    for code, line in sorted(lines.items()):
        original = []
        owned = []
        for start, end in pairwise(line["geometry"]):
            edge = tuple(sorted((tuple(start), tuple(end))))
            metres = hypot(*((end[i] - start[i]) * metres_per_degree[i] for i in (0, 1)))
            original.append(metres)
            owner = owners.get(edge)
            if owner is None:
                owners[edge] = code
                owned.append(metres)
            else:
                overlaps[(owner, code)] += metres
        route_lengths[code] = fsum(original) / 1000
        owned_lengths[code] = fsum(owned) / 1000
        if not isclose(route_lengths[code], line["one_way_km"], rel_tol=0, abs_tol=1e-7):
            raise ValueError(f"{code} line length and mapped geometry disagree")
    return route_lengths, owned_lengths, [
        {"first_work_package": first, "other_service": other, "km": metres / 1000}
        for (first, other), metres in sorted(overlaps.items())
    ]


def _orders(lines, route_lengths, owned_lengths, params, exclusion):
    orders = []
    d = params["delivery"]
    for code, line in sorted(lines.items()):
        length = owned_lengths[code]
        if length == 0:
            continue
        shared = not isclose(length, route_lengths[code], rel_tol=0, abs_tol=1e-7)
        if length < .02:
            orders.append({
                "section": code, "route_km": length, "selected_planning_method": "design_hold",
                "purpose": "New connection shorter than the standard civil evaluator's 20 m domain",
                "residual_bays_pending_design": 1, "residual_length_m": length * 1000,
                "calendar_days": None, "civil_scope_usd": dict.fromkeys(CASES),
            })
            continue
        bays = int(round(length, 9) * 1000 // erection.SPAN_M)
        advancing = [front - d["starter_bays_each_end"]
                     for front in erection.split_fronts(bays - d["meeting_bays"])]
        deck = (not line["loop"] and not shared and length >= .2
                and any(count > ceil(count * exclusion / 100) for count in advancing))
        order = network_delivery.section_order(
            code, length, "deck" if deck else "road",
            ("Two terminal delivery fronts" if deck else
             "Road access at an orbital, short connection or shared alignment"), exclusion,
        )
        order["route_km"] = length
        order["service_route_km"] = route_lengths[code]
        orders.append(order)
    return orders


def _standard_stock(orders, quantities, params):
    if not orders:
        return None, {}
    train = vehicle_audit.evaluate(cars=6, material="steel")
    family = family_comparison.evaluate_high_load(route_km=12, selected_family="U",
                                                  selected_span_m=erection.SPAN_M,
                                                  installed_vehicle=train)
    stock = next(row for row in family["rows"] if row["span_m"] == erection.SPAN_M
                 and row["section"]["shape"] == "U" and row["section"]["depth_m"] == 1.55
                 and row["shared_pier"])
    if {row["civil_physical_id"] for row in orders} != {stock["physical_id"]}:
        raise ValueError("The recurring stock geometry differs across construction packages")
    q, actions = stock["quantities"], stock["actions"]
    girders, supports = quantities["standard_girders"], quantities["standard_support_positions"]
    flatbed_axles = params["delivery"]["flatbed_axles"]
    loaded_flatbed = actions["mass_t"] + params["delivery"]["flatbed_tare_t"]
    result = dict(
        civil_stock_id=stock["physical_id"], retained_train_load_case_id=train["candidate_id"],
        girder_concrete_m3=q["full_standard_beam_concrete_m3"] / q["standard_beams"] * girders,
        girder_bare_mass_t=girders * actions["mass_t"],
        girder_bar_planning_t=q["standard_beam_bar_planning_kg"] / q["standard_beams"] * girders / 1000,
        girder_strand_t=q["standard_beam_strand_kg"] / q["standard_beams"] * girders / 1000,
        standard_support_concrete_m3=supports * stock["support"]["concrete_m3"],
        one_girder_bare_mass_t=actions["mass_t"], example_hook_demand_t=actions["chart_demand_t"],
        loaded_flatbed_t=loaded_flatbed, assumed_flatbed_axles=flatbed_axles,
        mean_loaded_flatbed_axle_t=loaded_flatbed / flatbed_axles,
        retained_high_operating_max_axle_t=max(family["load_cases"]["high"]["axle_kg_per_car"]) / 1000,
        basis="Recurring 20 m stock and spread footing trial only. Match supports and lift geometry to surveys.",
    )
    return result, family["member_sources"]


def _water_screen(lines):
    """Flag mapped water under the route at a maximum 20 m sample interval."""
    context = holistic_network.read(WATER_CONTEXT)
    intervals = []
    for code, line in sorted(lines.items()):
        track = holistic_network.Track(line["geometry"])
        count = ceil(track.km / .02)
        step = track.km / count
        chainage = (np.arange(count) + .5) * step
        wet = ~holistic_network.dry_points([track.at(km) for km in chainage], context)
        edges = np.flatnonzero(np.diff(np.r_[False, wet, False]))
        intervals.extend(dict(line=code, from_km=float(start * step), to_km=float(end * step),
                              screened_wet_length_m=float((end - start) * step * 1000))
                         for start, end in zip(edges[::2], edges[1::2], strict=True))
    return dict(
        sample_max_spacing_m=20, route_intervals=intervals,
        basis=("Geometry screen on retained mapped water polygons. Short canals, parallel basins, "
               "bridge length, approaches, high water and pier clearance require separate survey."),
    )


def _road_schedule(orders, road_teams):
    road = [row for row in orders if row["selected_planning_method"] == "road_day"]
    clocks = [0.] * min(road_teams, len(road))
    assignments = []
    for row in sorted(road, key=lambda row: (-row["calendar_days"], row["section"])):
        slot = min(range(len(clocks)), key=clocks.__getitem__)
        start = clocks[slot]
        clocks[slot] += row["calendar_days"]
        assignments.append(dict(section=row["section"], road_team=slot + 1, start_day=start,
                                finish_day=clocks[slot]))
    return clocks, assignments


def _programme(orders, launcher_pairs, road_teams, yard):
    # The retained deck programme reserves each pair for the whole corridor job.
    # Road delivery uses a separate pool of crews, cranes and concurrent shared
    # yards. Deck fallback crane shifts are carried by the deck packages.
    deck = network_delivery.slots(orders, launcher_pairs)
    road_clocks, road = _road_schedule(orders, road_teams)
    deck_finish = max((row["finish_day"] for row in deck["paired_line_programmes"]), default=0.)
    road_finish = max(road_clocks, default=0.)
    deck_slots, road_slots = deck["available_launcher_pairs"], len(road_clocks)
    yard_slots = deck_slots * 2 + road_slots
    return dict(
        paired_line_programmes=deck["paired_line_programmes"], road_line_programmes=road,
        active_launcher_pairs=deck_slots, concurrent_launcher_sets=2 * deck_slots,
        concurrent_construction_flatbeds=2 * deck_slots,
        active_road_day_teams=road_slots, shared_offsite_yards=road_slots,
        shared_offsite_yard_lease_days=fsum(road_clocks),
        concurrent_yard_sites=yard_slots, concurrent_yard_area_ha=yard_slots * yard["area_ha"],
        concurrent_moulds=yard_slots * yard["mould_count"],
        concurrent_released_stock_slots=yard_slots * yard["released_storage_slots"],
        shared_yard_joint_casting_release_per_day=road_slots * yard["releases_per_yard_day"],
        last_standard_deck_day=max(deck_finish, road_finish),
        last_deck_fed_package_day=deck_finish, last_road_package_day=road_finish,
        basis=("Relative calendar days with independent road teams and two-end launcher pairs. Each "
               "road team reserves one casting yard and each deck job reserves two terminal yards. "
               "Terminal yards are relocated by work package and the model retains mobilisation and "
               "site setup for every package. The held day/night and foundation-release scenarios, "
               "road permits and stock schedules require contractor evidence. The finish is a "
               "standard-deck handover envelope. Opening requires other programmes."),
        opening_date=None,
    )


def _workforce(orders, quantities, programme, params):
    shifts = defaultdict(int)
    for order in orders:
        for row in (*order["crew_shifts"], *order["casting_shifts"]):
            shifts[row["phase"], row["role"], row["shift"]] += row["paid_hours"]
    hours = {phase: sum(paid for key, paid in shifts.items() if key[0] == phase)
             for phase in ("rail-fed erection", "road erection and public haul", "casting yard")}
    erection_hours = hours["rail-fed erection"] + hours["road erection and public haul"]
    if erection_hours + hours["casting yard"] != sum(
        row["paid_total_method_and_casting_hours"] for row in orders
    ):
        raise ValueError("Crew shifts and priced work packages have different paid hours")
    productivity = line_benchmark_civil.PARAMETERS
    other = {}
    for i, case in enumerate(CASES):
        shifts_required = sum(
            ceil(1000 * row["double_track_km"] / productivity["rail_track_m_per_shift"][i])
            for row in quantities["route_register"]
        )
        track = shifts_required * productivity["rail_install_crew"][i] * erection.SHIFT_H
        support = quantities["standard_support_positions"] * productivity["support_field_h_each"][i]
        other[case] = dict(standard_support_productive_person_hours=support,
                           standard_support_paid_person_hours_at_75pct=support / .75,
                           permanent_track_paid_person_hours=track, permanent_track_shifts=shifts_required)
    deck_fronts = 2 * programme["active_launcher_pairs"]
    road_fronts = programme["active_road_day_teams"]
    return dict(
        paid_erection_hours=erection_hours, paid_rail_fed_erection_hours=hours["rail-fed erection"],
        paid_road_erection_and_haul_hours=hours["road erection and public haul"],
        paid_casting_hours=hours["casting yard"],
        paid_deck_and_casting_hours=erection_hours + hours["casting yard"],
        crew_shifts=[dict(phase=phase, role=role, shift=shift, paid_hours=paid)
                     for (phase, role, shift), paid in sorted(shifts.items())],
        peak_covered_posts_envelope=dict(
            gantry_team_per_shift=deck_fronts * sum(params["rail_crew"].values()),
            road_and_haul_day=(road_fronts + deck_fronts) * sum(params["road_crew"].values()),
            casting_day=programme["concurrent_yard_sites"] * sum(params["yard_crew"].values()),
        ),
        additional_standard_support_and_track_planning_hours=other,
        labour_basis=("Crew availability covers posts and paid shift hours. Gantry payroll is priced "
                      "once in erection, road labour in operated plant and haul, casting labour in "
                      "fabrication, and indicative standard support and permanent track labour in "
                      "their works allowances. Support and track figures transfer outline productivity "
                      "assumptions. Station, utility, special-crossing, testing and operations crews "
                      "require separate contractor or operator workplans."),
    )


def _costs(quantities, orders, programme, params, policy, evidence, fx):
    yard = erection.yard_layout(params)
    d, prices = params["delivery"], params["prices"]
    route_rates = policy["route"]
    station_rates = policy["stations"]
    rail, road = evidence["rail"], evidence["corridor"]
    track_anchor = rail["renewal_estimate_usd"] / rail["renewal_km"] / 1e6
    corridor_anchor = road["comparator_iqd"] / fx / road["comparator_km"] / 1e6
    bearing = family_comparison.TRIALS
    costs = {}
    for i, case in enumerate(CASES):
        road_yards = programme["shared_offsite_yards"]
        offsite = {
            "forms": road_yards * d["moulds_per_yard"] * bearing["bed_and_form_usd"][i]
                     * (erection.SPAN_M / 10) ** .8 / 1e6,
            "hardstand": road_yards * yard["area_m2"] * prices["yard_temporary_hardstand_usd_m2"][i] / 1e6,
            "elapsed_lease": programme["shared_offsite_yard_lease_days"] * yard["area_m2"]
                             * prices["yard_temporary_land_lease_usd_m2_day"][i] / 1e6,
        }
        elevated = sum(row["civil_scope_usd"][case] for row in orders) / 1e6 + sum(offsite.values())
        matched_road_elevated = (sum(row["road_day_civil_scope_usd"][case] for row in orders) / 1e6
                                 + sum(offsite.values()))
        station = {
            "line_civil_and_finishes": quantities["station_line_platform_packages"]
                                       * station_rates["civil_and_finishes"][i],
            "line_electromechanical_and_platform_equipment": quantities["station_line_platform_packages"]
                                                             * station_rates["electromechanical_and_platform_equipment"][i],
            "site_public_access_egress": quantities["station_sites"] * station_rates["public_access_and_egress"][i],
            "transfer_circulation_allowance": quantities["transfer_sites"] * station_rates["public_access_and_egress"][i],
            "street_transfer_access_allowance": quantities["street_transfer_links"]
                                                * station_rates["public_access_and_egress"][i],
        }
        scope = {
            "elevated_civil": elevated,
            "stations_access": sum(station.values()),
            "track_walkways": quantities["double_track_km"] * track_anchor
                              * route_rates["track_walkway_factor_on_iraq_renewal"][i],
            "land_utilities_disruption": quantities["unique_guideway_km"] * corridor_anchor
                                        * route_rates["land_utilities_share_of_baghdad_road_per_km"][i],
        }
        direct = sum(scope.values())
        bearings, girders = quantities["standard_bearings"], quantities["standard_girders"]
        costs[case] = dict(
            scope_usd_m=scope, direct_usd_m=direct, direct_iqd_trillion=direct * fx / 1e6,
            matched_road_direct_usd_m=direct - elevated + matched_road_elevated,
            matched_road_elevated_civil_usd_m=matched_road_elevated,
            embedded_residual_interface_allowance_usd_m=len(
                [row for row in orders if row["residual_bays_pending_design"]]
            ) * prices["residual_interfaces_usd"][i] / 1e6,
            offsite_yards_in_elevated_scope_usd_m=offsite, station_scope_usd_m=station,
            annual_civil_inspection_usd_m=(bearings * bearing["annual_inspection_usd_bearing"][i]
                                           + girders * bearing["inspection_usd_span_year"][i]) / 1e6,
            year20_bearing_renewal_usd_m=bearings * (bearing["bearing_purchase_usd_each"][i]
                                                   + bearing["bearing_renewal_labour_usd"][i]) / 1e6,
        )
    return costs


def evaluate(network, *, launcher_pairs=3, road_teams=2, overhead_exclusion_pct=None):
    """Reprice the mapped candidate with retained unit sources and a conditional resource plan."""
    if any(type(value) is not int or value < 1 for value in (launcher_pairs, road_teams)):
        raise ValueError("The programme requires positive whole launcher-pair and road-team counts")
    if not network["lines"] or not network["stations"]:
        raise ValueError("A delivery candidate requires mapped lines and station sites")
    network_id = holistic_network._identity(dict(network))
    if any(network_id[key] != network[key] for key in ("candidate_id", "evaluation_id")):
        raise ValueError("The delivery inputs have changed since the network map was evaluated")
    if holistic_network.validate(network) != network["topology"]:
        raise ValueError("Mapped network topology and station register disagree")
    params = erection.load_assumptions()
    exclusion = params["delivery"]["overhead_exclusion_pct"] if overhead_exclusion_pct is None else overhead_exclusion_pct
    if not 0 <= exclusion <= 100:
        raise ValueError("Overhead exclusion must be a percentage between zero and 100")
    route_lengths, owned_lengths, overlaps = _length_register(network["lines"])
    orders = _orders(network["lines"], route_lengths, owned_lengths, params, exclusion)
    priced = [row for row in orders if row["calendar_days"] is not None]
    yard = erection.yard_layout(params)
    programme = _programme(priced, launcher_pairs, road_teams, yard)
    quantities = {
        "service_route_km": fsum(route_lengths.values()),
        "unique_guideway_km": fsum(owned_lengths.values()),
        "service_overlap_km": fsum(row["km"] for row in overlaps),
        "double_track_km": 2 * fsum(owned_lengths.values()),
        "station_sites": len(network["stations"]),
        "transfer_sites": len(network["transfers"]),
        "street_transfer_links": len(network.get("station_site_links", [])),
        "station_line_platform_packages": sum(len(row["station_ids"]) for row in network["lines"].values()),
        "tunnel_km": 0,
        "underground_stations": 0,
        "route_register": [
            dict(line=code, service_route_km=route_lengths[code], unique_guideway_km=length,
                 service_overlap_km=route_lengths[code] - length, double_track_km=2 * length,
                 station_line_platform_packages=len(network["lines"][code]["station_ids"]),
                 transfer_station_calls=sum(len(network["stations"][site]["lines"]) > 1
                                            for site in network["lines"][code]["station_ids"]))
            for code, length in owned_lengths.items()
        ],
        "overlap_register": overlaps,
    }
    for key in ("standard_bays", "standard_girders", "standard_support_positions", "standard_bearings",
                "residual_bays_pending_design", "residual_length_m", "dedicated_yards", "launcher_sets",
                "flatbeds", "loaded_beam_trips", "road_day_loaded_beam_trips", "erection_lane_hours",
                "road_day_erection_lane_hours", "temporary_track_km"):
        quantities[key] = sum(row.get(key, 0) for row in orders)
    if not isclose(quantities["unique_guideway_km"] + quantities["service_overlap_km"],
                   quantities["service_route_km"], rel_tol=0, abs_tol=1e-7):
        raise ValueError("Guideway plus allocated overlap must reconcile to mapped service route length")
    quantities["standard_stock_materials"], stock_sources = _standard_stock(priced, quantities, params)
    quantities["water_screen"] = _water_screen(network["lines"])
    fx = iraq_power.read_toml("iraq-market.toml")["currency"]["iqd_per_usd"]
    paths = [Path(__file__), Path(holistic_network.__file__), Path(network_delivery.__file__),
             Path(erection.__file__), erection.ASSUMPTIONS, Path(family_comparison.__file__),
             Path(vehicle_audit.__file__), WATER_CONTEXT,
             Path(line_benchmark_civil.__file__), CITY / "iraq-capital.toml", CITY / "airport-works.toml",
             CITY / "iraq-market.toml", CITY / "engineering/prototype/shop-rates.toml"]
    result = dict(
        schema="osr.baghdad.residential-delivery.v1", candidate_id=network["candidate_id"],
        network_evaluation_id=network["evaluation_id"], quantities=quantities, orders=orders,
        programme=programme, workforce=_workforce(priced, quantities, programme, params),
        cost_cases=_costs(quantities, priced, programme, params,
                          iraq_power.read_toml("iraq-capital.toml"),
                          iraq_power.read_toml("airport-works.toml"), fx),
        assumptions=dict(span_m=erection.SPAN_M, planning_launcher_pairs=launcher_pairs,
                         planning_road_teams=road_teams, overhead_exclusion_pct=exclusion, iqd_per_usd=fx,
                         source_yard_layout=yard),
        conditional_shared_running=bool(overlaps), physical_accepted=False,
        source_sha256={**stock_sources, **{str(path.resolve().relative_to(ROOT)): sha256(path.read_bytes()).hexdigest()
                                          for path in paths}},
        cost_scope=("Standard elevated carrying deck and supplies include residual interface allowances "
                    "and temporary works. Iraqi benchmarks price incremental station civil, finishes and "
                    "equipment per served line over the common carrying deck, street access once per site, "
                    "and one additional access-package equivalent for transfer circulation at each site. "
                    "Track/walkways cover the permanent running way, while erection track is temporary "
                    "and recovered. The corridor land/utilities allowance concerns property, diversions "
                    "and public disruption beyond booked erection lanes and separately leased yards. "
                    "The matched road comparator retains the source's two local yards on eligible open "
                    "sections. All three prices are budget hypotheses in constant 2026 money. Apply "
                    "project design, commissioning and contingency once on the integrated capital ledger."),
        holds=[
            "Identify approved land, utilities, gradients, site drainage, foundations and local construction access.",
            "Measure bridge, grade separation, station transition, river and special span quantities and quote whole packages.",
            "Resolve station deck/foundation boundaries and temporary running continuity from measured station footprints.",
            "Approve capacity and junctions for any genuinely shared guideway. Coincidence here is identical mapped vertices with no proximity merge.",
            "Resolve physical gaps created by shared-edge allocation. A road work package uses its net length-equivalent.",
            "Check terminal and shared yard land, crane chart at working radius, carrier/gantry deck loading, traffic windows and shifts. The retained loaded-flatbed mean axle exceeds the high operating maximum.",
            "Obtain schedules for the stations, utility diversions, track, depot, power, systems, checks and passenger opening.",
        ],
        unpriced_order_ids=[row["section"] for row in orders if row["calendar_days"] is None],
    )
    result["evaluation_id"] = sha256(holistic_network.encode(result)).hexdigest()
    return result
