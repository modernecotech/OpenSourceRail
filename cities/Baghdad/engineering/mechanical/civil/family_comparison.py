"""Size and price straight, double-track viaduct options on one train load case."""
import argparse
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from hashlib import sha256
import json
from math import ceil
from pathlib import Path
import tomllib

from cities.Baghdad.engineering.prototype.weights import moving_span
from cities.Baghdad.engineering.simulation import vehicle_civil as vehicle
from engineering.performance import disk_reservation

HERE = Path(__file__).resolve().parent
CITY = HERE.parents[2]
ROOT = CITY.parents[1]
SPAN_OPTIONS = (10, 15, 20, 25, 30)
# Trial dimensions in metres. U webs stand above the rail seat. End thickenings
# are BELOW the U floor and retain the free running channel. All sections are
# symmetric in y. A rail-seat, drainage, escape and curve fit is still required.
U_DEPTH = {10: 0.95, 15: 1.12, 20: 1.35, 25: 1.62, 30: 1.92}
U_WEB = {10: .17, 15: .18, 20: .20, 25: .22, 30: .24}
U_SLAB = {10: .20, 15: .22, 20: .24, 25: .26, 30: .28}
CASES = ("low", "base", "high")
TRIALS = {
    "track_pitch_m": 4.5, "braking_m_s2": 1., "grade_fraction": .02,
    "allowable_release_tension_mpa": 1.5, "allowable_release_compression_mpa": 18.,
    "rigging_t": 4., "lift_dynamic_factor": 1.10, "lift_radius_m": 12.,
    "cost_discount_real": .04, "rebar_kg_per_m3": 130., "strand_usd_kg": [1.3, 1.9, 3.1],
    "bearing_purchase_usd_each": [180., 450., 1400.], "closure_usd_shift": [500., 2400., 9500.],
    "annual_inspection_usd_bearing": [4., 12., 45.], "bearing_renewal_labour_usd": [250., 800., 2400.],
    "inspection_usd_span_year": [12., 40., 130.], "inspection_usd_pt_joint_year": [30., 100., 400.],
    "bed_and_form_usd": [75000., 160000., 360000.], "match_cast_joint_usd": [1900., 5800., 17000.],
    "staged_pt_per_girder_usd": [1300., 3300., 8600.], "duct_grout_stressing_usd_per_strand_m": [.9, 1.8, 4.2],
    "temporary_tower_cycle_usd": [1600., 5000., 16000.], "material_delivery_multiplier": [1.0, 1.25, 1.65],
}
SOURCE_LINK = "https://backend.delhimetrorail.com/documents/8790/OUTLINE_CONSTRUCTION_SPECIFICATIONS_for_Civil_Works_Revision-R4_June_2025.pdf"


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def read_toml(path):
    return tomllib.loads(path.read_text())


def section(kind, length, extra_depth, box):
    if kind == "issued-box":
        b, h, web, slab = (box[k] for k in ("width_m", "depth_m", "web_m", "slab_m"))
    elif kind == "joined-box":
        b, h, web, slab = 2.20, 1.55 + extra_depth, .22, .23
    else:
        web = U_WEB[length]
        b, h, slab = 3.60 + 2 * web, U_DEPTH[length] + extra_depth, U_SLAB[length]
    closed = kind != "U"
    inner_h = h - slab * (2 if closed else 1)
    inner_w = b - 2 * web
    area = b*h - inner_w*inner_h
    void_z = slab + inner_h/2
    z = (b*h*h/2 - inner_w*inner_h*void_z) / area
    inertia = (b*h**3 / 12 + b*h*(h/2-z)**2
               - inner_w*inner_h**3 / 12 - inner_w*inner_h*(void_z-z)**2)
    # Two end diaphragms; the segmental box includes local concrete on BOTH mating faces.
    extra = 2 * .55 * (inner_w*inner_h if closed else b*.18)
    if kind == "joined-box":
        extra += .4 * inner_w * inner_h
    return dict(shape=kind, staged_post_tension=(kind == "U" and extra_depth > 0), width_m=b, depth_m=h, web_m=web, floor_m=slab, cg_m=z, area_m2=area,
                inertia_m4=inertia, volume_m3=length*area+extra, local_thickening_m3=extra,
                clear_channel_m=inner_w if not closed else None)


def engineering(length, sec, axle_actions, cage, cfg):
    box, mat = cfg["box"], cfg["materials"]
    rho = mat["rc_unit_weight_kn_m3"]
    g = mat["gravity_m_s2"]
    live = axle_actions[length]
    span = length - .5
    area, inertia, z, h = (sec[k] for k in ("area_m2", "inertia_m4", "cg_m", "depth_m"))
    bottom, top = inertia/z, inertia/(h-z)
    # Apply the central joint thickening as a point weight at midspan. Other
    # additional end concrete is conservatively smeared over the bearing span.
    joint_m3 = .4*(sec["width_m"]-2*sec["web_m"])*(h-2*sec["floor_m"]) if sec["shape"] == "joined-box" else 0.
    bare_kn = sec["volume_m3"] * rho
    dead_m = ((bare_kn-joint_m3*rho)/span + box["superimposed_dead_kn_m"])*span**2/8 + joint_m3*rho*span/4
    moment = dead_m + box["moving_load_factor"]*live["max_moment"]["value"]
    reaction_dead = (bare_kn + box["superimposed_dead_kn_m"]*length)/2
    reaction_live = box["moving_load_factor"]*live["max_reaction"]["value"]
    reaction = reaction_dead + reaction_live
    # Select whole paired 15.2 mm strands from the parent force and loss range.
    tendon = cage["strand"]
    fp = tendon["catalogue_minimum_breaking_kn"] * tendon["studied_initial_force_fraction"]
    e = .30 if sec["shape"] == "issued-box" else z - .12
    loss = max(tendon["assumed_losses"])
    required = moment / (bottom/area + e)
    strands = tendon["strand_count"] if sec["shape"] == "issued-box" else max(4, 2*ceil(required/(2*fp*(1-loss))))
    installed = strands * fp
    def fibres(force, bending, ecc=e):
        return [(force/area + (bending-force*ecc)/top)/1000,
                (force/area - (bending-force*ecc)/bottom)/1000]
    # Treat the additional concrete at outer diaphragms and segment joints as
    # point weights at their centroids. Both lie outside the pickup positions.
    segments = 2 if sec["shape"] == "joined-box" else 1
    unit_length = length / segments
    uniform = sec["area_m2"] * rho
    staged = sec["staged_post_tension"]
    pick_fraction = .08 if staged else .20
    left_pick = pick_fraction*unit_length
    right_pick = unit_length-left_pick
    end_weight = (sec["local_thickening_m3"]-joint_m3)*rho/2
    end_loads = [(end_weight, .275), (end_weight, unit_length-.275) if segments == 1
                 else (joint_m3*rho/2, unit_length-.10)]
    right_reaction = (uniform*unit_length*(unit_length/2-left_pick)
                      + sum(w*(x-left_pick) for w,x in end_loads))/(right_pick-left_pick)
    left_reaction = bare_kn/segments-right_reaction
    peak_x = min(right_pick, max(left_pick, (left_reaction-end_weight)/uniform))
    lift_moments = [TRIALS["lift_dynamic_factor"]*(
        left_reaction*max(x-left_pick, 0) - uniform*x**2/2
        - sum(w*max(x-pos, 0) for w,pos in end_loads)) for x in (left_pick, peak_x, right_pick)]
    # Match-cast halves lifted as reinforced concrete; full PT first acts on falsework.
    # One construction alternative: approximately 30% pretension for handling;
    # paired strands, remaining force applied in profiled tendons after landing.
    early_strands = 2*round(.30*strands/2) if staged else strands if segments == 1 else 0
    lift_force = early_strands*fp
    lift_stresses = [s for m in lift_moments for s in fibres(lift_force, m)]
    # Service is checked at midspan. Transfer is checked with end supports and
    # self-weight, with full tendon eccentricity at midspan and graded to zero at ends.
    bare_m = dead_m - box["superimposed_dead_kn_m"]*span**2/8
    transfer = fibres(installed, bare_m)
    if staged:
        lift_stresses.extend(fibres(lift_force, bare_m))
        # Full PT end anchor result acts at cg, straight initial strands stay low.
        transfer.extend(fibres(installed, 0., e*early_strands/strands))
    elif segments == 2:
        transfer.extend(fibres(installed, 0., 0.))
        # If the centre tower remains engaged while applying all the PT, full
        # midspan gravity bending cannot be credited at the match-cast joint.
        transfer.extend(fibres(installed, 0., e))
    service = fibres(installed*(1-loss), moment)
    torque = reaction_live*box["live_lateral_eccentricity_m"]
    side = .65 if sec["shape"] != "U" else 1.40
    min_vertical = reaction_dead + box["moving_load_factor"]*live["min_reaction"]["value"]
    min_bearing = (min_vertical-abs(torque/side))/2
    shear_legs_mm2_per_m = 1000 * reaction / (.8*h*435.)  # V=z*(Asw/s)*fy; neglect concrete
    mass_t = bare_kn / g
    charged_lift = TRIALS["lift_dynamic_factor"] * (mass_t/segments + TRIALS["rigging_t"])
    chart = 60 if charged_lift <= 60 else 110 if charged_lift <= 110 else 180
    # Group widths for a proposed strand grid; this excludes couplers/ducts and splice bars.
    # Straight pretension fits across the U floor; post-tension ducts/anchors
    # need actual detailing. Keep the issued box grid and its measured datum.
    floor_width = sec["width_m"] - .22
    strands_per_row = max(1, int(floor_width/.07) + 1)
    floor_rows = ceil(early_strands / strands_per_row)
    holds = ["Ultimate flexure, shear/torsion interaction, dynamic stiffness, fatigue and end-zone reinforcement",
             "Surveyed gauge, rail alignment, conductor clearances, differential settlement and drainage",
             "Signed lift chart, sling imbalance, wind, hauling axle loads and contractor stability method"]
    if sec["shape"] == "U":
        holds.append("Open U lateral distortion and diaphragm-to-web transfer during transport and lift")
    if segments == 2:
        holds.append("RC segment lifting, temporary cross-bracing/tower, PT anchorages, shear keys, grout and joint fatigue")
    checks = dict(service_bottom_compression=service[1] >= 0, release_fibre_min=min(transfer) >= -TRIALS["allowable_release_tension_mpa"],
                  release_fibre_max=max(transfer) <= TRIALS["allowable_release_compression_mpa"],
                  lift_fibre_min=min(lift_stresses) >= -TRIALS["allowable_release_tension_mpa"],
                  lift_fibre_max=max(lift_stresses) <= TRIALS["allowable_release_compression_mpa"],
                  lifting_capacity=charged_lift <= chart, positive_bearing_reactions=min_bearing > 0)
    return dict(moment_knm=moment, dead_moment_knm=dead_m, peak_track_reaction_kn=reaction,
                dead_track_reaction_kn=reaction_dead, dynamic_live_reaction_kn=reaction_live, end_torque_knm=torque,
                bearing_offset_m=side, peak_bearing_kn=(reaction+torque/side)/2, min_bearing_at_peak_torque_kn=(reaction-torque/side)/2,
                minimum_bearing_independent_envelopes_kn=min_bearing,
                strand_count=strands, straight_handling_strands=early_strands, straight_floor_rows_trial=floor_rows if sec["shape"]=="U" else None,
                pick_inset_m=left_pick, handling_moments_knm=lift_moments, profiled_second_stage=staged, initial_force_kn=installed,
                tendon_eccentricity_m=e, bottom_no_tension_required_effective_kn=required, loss_fraction=loss,
                service_top_bottom_compression_mpa=service, transfer_top_bottom_compression_mpa=transfer,
                lift_min_compression_mpa=min(lift_stresses), lift_max_compression_mpa=max(lift_stresses),
                gravity_deflection_upper_mm=moment*span**2/(8*box["concrete_elastic_modulus_gpa"]*1e6*inertia)*1000,
                shear_links_demand_mm2_per_m=shear_legs_mm2_per_m, axle_reaction_envelope=live,
                mass_t=mass_t, handling_unit_t=mass_t/segments, chart_demand_t=charged_lift,
                tower_reaction_two_halves_kn=2*(uniform*unit_length/2
                    + sum(w*x for w,x in end_loads)/unit_length) if segments == 2 else None,
                chart_class_t_at_12m=chart, segments=segments, checks=checks, holds=holds)


def support(a, shared, soil, cfg):
    # Bounding interior bent: both adjoining spans' independent maximum end reactions.
    tracks = 2 if shared else 1
    pitch = TRIALS["track_pitch_m"]
    # Preserve a 0.25 m trial edge outside each complete pad and the original
    # 10 m box crosshead width. Widen the U support for its actual pad spacing.
    track_head = max(cfg["pier"]["cap_width_m"], 2*a["bearing_offset_m"]+cfg["box"]["pad_width_m"]+.50)
    cap_length, cap_width, cap_depth = (pitch+track_head, 1.6, 1.25) if shared else (track_head, 1.4, .7)
    column = 1.4 if shared else 1.
    height = cfg["pier"]["column_height_m"]
    sub = cap_length*cap_width*cap_depth + column**2*height
    dead = 2*a["dead_track_reaction_kn"]
    live = 2*a["dynamic_live_reaction_kn"]
    # Horizontal braking from both adjacent live-load upper bounds. Check both
    # loaded tracks as well as transverse overturning with one loaded track.
    horizontal_ratio = TRIALS["braking_m_s2"]/cfg["materials"]["gravity_m_s2"] + TRIALS["grade_fraction"]
    for i in range(10, 101):
        side = i*.25
        depth = max(1., .25*ceil(side/4/.25))
        footing = side**2*depth
        pressures = []
        for active in range(1,tracks+1):
            normal = (sub+footing)*25 + dead*tracks + live*active
            brake_moment = live*active*horizontal_ratio*(depth+height+cap_depth)
            lateral_moment = (live*pitch/2 if shared and active == 1 else 0) + 2*active*abs(a["end_torque_knm"])
            amplitude = 6*(brake_moment+lateral_moment)/side**3
            pressures.extend((normal/side**2-amplitude, normal/side**2+amplitude))
        if min(pressures) >= 0 and max(pressures) <= soil:
            break
    else:
        raise ValueError("No compressive shallow footing fits the study envelope")
    lateral_footing_gap = None if shared else pitch-side
    return dict(footing_width_m=side, footing_depth_m=depth, concrete_m3=sub+footing,
                cap_cross_track_m=cap_length, cap_along_track_m=cap_width, cap_depth_m=cap_depth,
                cap_outer_pad_edge_margin_m=(track_head-2*a["bearing_offset_m"]-cfg["box"]["pad_width_m"])/2,
                footing_clear_gap_m=lateral_footing_gap, independent_footings_clear=shared or lateral_footing_gap > 0,
                peak_soil_kpa=max(pressures), minimum_soil_kpa=min(pressures),
                full_bent_longitudinal_braking_kn=live*tracks*horizontal_ratio,
                full_bent_bound_end_twist_knm=2*tracks*abs(a["end_torque_knm"]),
                crosshead_cantilever_knm=(dead+live)*pitch/2+2*abs(a["end_torque_knm"]) if shared else None)


def cost(row, rates, shop, basket):
    n, p, bears, placements = (row[k] for k in ("beams", "supports", "bearings", "placements"))
    a, sec, base = row["actions"], row["section"], row["support"]
    length = row["span_m"]
    options = {}
    for i, name in enumerate(CASES):
        # Material allowances bought separately from fabrication, site works and haul labour.
        vol = n*sec["volume_m3"]+p*base["concrete_m3"]
        if sec["shape"] == "issued-box":
            beam_steel = row["counted_bar_kg_per_beam"]
        else:
            # Budget includes extra cage steel for links; supplier must return a cage schedule.
            beam_steel = sec["volume_m3"]*TRIALS["rebar_kg_per_m3"] + a["shear_links_demand_mm2_per_m"]*1e-6*7850*length*sec["depth_m"]
        steel = n*beam_steel+p*base["concrete_m3"]*rates["rebar_t_per_m3"][i]*1000
        strand_kg = n*a["strand_count"]*length*row["strand_kg_m"]
        chart_factor = {60: 1., 110: 1.65, 180: 2.8}[a["chart_class_t_at_12m"]]
        closure_shifts = ceil(placements / row["placements_per_shift"])
        yard_size = min(8, placements)
        # Labour and yard handling estimated against issue's first 10m delivery allowance,
        # less its stated modelled standard haul. Variants scale with casting and set-ups.
        haul_rate = shop["civil-haul"]["usd"][i]
        fabrication = (rates["beam_fabrication_and_delivery_usd_each"][i]-haul_rate) * (
            .50*placements+.50*n*sec["volume_m3"]/13.404)
        overhead = rates["other_civil_usd_m_per_route_km"][i]*1e6*row["route_km"]
        parts = dict(materials=vol*basket["concrete"]*TRIALS["material_delivery_multiplier"][i]
                     +steel*basket["bar"]/1000 + strand_kg*TRIALS["strand_usd_kg"][i],
                     fabrication=fabrication, haul=placements*haul_rate*chart_factor,
                     supports=p*rates["support_works_usd_each"][i]*(1.25 if row["shared_pier"] else 1.),
                     bearing_supply_and_install=bears*(TRIALS["bearing_purchase_usd_each"][i]+shop["civil-bearing"]["usd"][i]),
                     erection=placements*rates["lift_usd_each"][i]*chart_factor,
                     road_occupation=closure_shifts*TRIALS["closure_usd_shift"][i],
                     forms=yard_size*TRIALS["bed_and_form_usd"][i]*(length/a["segments"]/10)**.8,
                     common_elevated_scope=overhead)
        if a["profiled_second_stage"]:
            parts["stressed_after_landing"] = n*(TRIALS["staged_pt_per_girder_usd"][i]+
                (a["strand_count"]-a["straight_handling_strands"])*length*TRIALS["duct_grout_stressing_usd_per_strand_m"][i])
        if a["segments"] > 1:
            parts["temporary_tower_and_joint"] = n*(TRIALS["temporary_tower_cycle_usd"][i]+TRIALS["match_cast_joint_usd"][i]
                +TRIALS["staged_pt_per_girder_usd"][i]+a["strand_count"]*length*TRIALS["duct_grout_stressing_usd_per_strand_m"][i])
        annual = bears*TRIALS["annual_inspection_usd_bearing"][i]+n*TRIALS["inspection_usd_span_year"][i]
        annual += (placements-n)*TRIALS["inspection_usd_pt_joint_year"][i]
        renew = bears*(TRIALS["bearing_purchase_usd_each"][i]+TRIALS["bearing_renewal_labour_usd"][i])
        rate = TRIALS["cost_discount_real"]
        installed = sum(parts.values())
        pv = installed + annual*(1-(1+rate)**-30)/rate + renew/(1+rate)**20
        options[name] = dict(installed_usd=installed, annual_inspection_usd=annual, year20_bearings_usd=renew,
                             lifecycle_pv_usd=pv, installed_breakdown_usd=parts)
    return options


def evaluate(route_km=12., cars=6, material="steel", soil_kpa=200, crane_limit_t=180):
    if crane_limit_t not in (60, 110, 180):
        raise ValueError("Use a priced crane capacity of 60, 110 or 180 t at 12 m radius")
    route_decimal = Decimal(str(route_km))
    if not route_decimal.is_finite() or not 0 < route_decimal <= 1000 or cars not in (3, 6) or material not in vehicle.MATERIAL or soil_kpa not in (150, 200, 250):
        raise ValueError("Use 0–1000 route-km, 3 or 6 cars, a supported body, and 150/200/250 kPa soil trial")
    route_m = Fraction(route_decimal)*1000
    route_km = float(route_decimal)
    cfg = read_toml(HERE/"concept.toml")
    sys = read_toml(CITY/"system.toml")
    rates = read_toml(CITY/"iraq-capital.toml")["civil"]
    shop = read_toml(vehicle.PROTOTYPE/"shop-rates.toml")["rates"]
    market = read_toml(CITY/"airport-works.toml")["materials"]
    exchange = read_toml(CITY/"iraq-market.toml")["currency"]["iqd_per_usd"]
    basket = dict(concrete=(rates["cement_t_per_m3"]*market["resistant_cement_iqd_t"]
                            + rates["gravel_m3_per_m3"]*market["crushed_gravel_iqd_m3"]
                            + rates["sand_m3_per_m3"]*market["sand_iqd_m3"])/exchange,
                  bar=market["reinforcing_steel_iqd_t"]/exchange)
    record, cage, bogie = vehicle.article_data()
    load = vehicle.load_case(record, bogie, sys["service_power"], cars, material, "central")
    axles = [(f"C{i+1}-A{j+1}", cx+dx, kg*cfg["materials"]["gravity_m_s2"]/1000)
             for i, cx in enumerate(record["interfaces"]["formation_body_from_car_x_m"][:cars])
             for j, (dx, kg) in enumerate(zip(record["interfaces"]["body_from_axle_x_m"], load["axle_kg_per_car"]))]
    moving = {l: moving_span(axles, l-.5, .25) for l in SPAN_OPTIONS}
    designs = [("issued-box", 10, 0)] + [("U", l, d) for l in SPAN_OPTIONS for d in (0, .20)]
    designs += [("joined-box", 20, 0), ("joined-box", 20, .20)]
    rows = []
    for kind, length, extra in designs:
        sec = section(kind, length, extra, cfg["box"])
        a = engineering(length, sec, moving, cage, cfg)
        full_bays, closure = divmod(route_m, length)
        bays = full_bays + bool(closure)
        for shared in (False, True):
            base = support(a, shared, soil_kpa, cfg)
            piers = (bays+1)*(1 if shared else 2)
            segments = a["segments"]
            row = dict(label=f"{length}m {kind} {sec['depth_m']:.2f}m / {'shared' if shared else 'separate'}",
                       span_m=length, section=sec, shared_pier=shared, route_km=route_km, actions=a, support=base,
                       beams=2*bays, supports=piers, bearings=8*bays, placements=2*bays*segments,
                       strand_kg_m=cage["strand"]["catalogue_linear_mass_kg_m"],
                       counted_bar_kg_per_beam=cage["straight_and_developed_bar_kg"] if kind == "issued-box" else None)
            row["closure_bay_m"] = float(closure) if closure else None
            row["ordered_excess_length_per_track_m"] = float(bays*length-route_m)
            row["checks"] = dict(a["checks"], independent_footings_clear=base["independent_footings_clear"],
                                 available_crane=a["chart_class_t_at_12m"] <= crane_limit_t,
                                 full_length_standard_bays=closure == 0)
            row["placements_per_shift"] = {60: 8, 110: 4, 180: 2}[a["chart_class_t_at_12m"]]
            row["haul_trips"] = row["placements"]
            row["traffic_shifts"] = ceil(row["placements"]/row["placements_per_shift"])
            row["mould_positions"] = min(8,row["placements"])
            row["casting_days_at_24h_cycle"] = ceil(row["placements"]/row["mould_positions"])
            row["casting_days_at_48h_cycle"] = 2*row["casting_days_at_24h_cycle"]
            row["source_train_candidate_id"] = record["candidate_id"]
            row["physical_id"] = digest(dict(section=sec, length=length, strands=a["strand_count"], strand_e=a["tendon_eccentricity_m"],
                                              footing=[base["footing_width_m"], base["footing_depth_m"]],
                                              crosshead=[base["cap_cross_track_m"], base["cap_along_track_m"], base["cap_depth_m"]],
                                              shared=shared, pier_height=cfg["pier"]["column_height_m"],
                                              tracks_pitch=TRIALS["track_pitch_m"], segments=segments, source_cage=cage["physical_id"]))
            row["priced_cases"] = cost(row, rates, shop, basket)
            row["soil_sensitivity"] = {}
            for soil in (150, 200, 250):
                alt_support = support(a, shared, soil, cfg)
                alt_cost = cost(dict(row, support=alt_support), rates, shop, basket)["base"]
                row["soil_sensitivity"][str(soil)] = {
                    "footing_width_m": alt_support["footing_width_m"],
                    "footing_clear_gap_m": alt_support["footing_clear_gap_m"],
                    "independent_footings_clear": alt_support["independent_footings_clear"],
                    "installed_usd_per_km": alt_cost["installed_usd"]/route_km,
                    "lifecycle_pv_usd_per_km": alt_cost["lifecycle_pv_usd"]/route_km,
                }
            row["complete_installed_usd"] = None
            row["eligible_for_selection"] = False
            rows.append(row)
    ref = rows[0]["priced_cases"]["base"]
    for row in rows:
        base = row["priced_cases"]["base"]
        row["base_installed_headroom_per_placement_usd"] = (ref["installed_usd"]-base["installed_usd"])/row["placements"]
        row["base_pv_change_vs_reference_usd"] = base["lifecycle_pv_usd"]-ref["lifecycle_pv_usd"]
    files = [Path(__file__), Path(vehicle.__file__), Path(__import__(moving_span.__module__, fromlist=["x"]).__file__),
             HERE/"concept.toml", CITY/"system.toml", CITY/"iraq-capital.toml", CITY/"airport-works.toml", CITY/"iraq-market.toml",
             vehicle.PROTOTYPE/"shop-rates.toml", vehicle.PROTOTYPE/"airport-prototype.zip"]
    sources = {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in files}
    screened = [r for r in rows if all(r["checks"].values())]
    quotations = {}
    for case in CASES:
        if screened:
            leader = min(screened, key=lambda r: r["priced_cases"][case]["lifecycle_pv_usd"])
            prices = leader["priced_cases"][case]
            quotations[case] = dict(label=leader["label"], physical_id=leader["physical_id"],
                                    installed_usd=prices["installed_usd"], lifecycle_pv_usd=prices["lifecycle_pv_usd"])
        else:
            quotations[case] = None
    decimal_text = format(route_decimal, "f")
    report = dict(schema="viaduct-family-comparison/1", route_km=route_km,
                  route_km_decimal=decimal_text.rstrip("0").rstrip(".") if "." in decimal_text else decimal_text,
                  cars=cars, material=material, soil_kpa=soil_kpa, crane_limit_t_at_12m=crane_limit_t,
                  passing_trial_count=len(screened), quotation_leaders=quotations,
                  passenger_train_kg=load["loaded_train_kg"], axle_count=len(axles), member_sources=sources, trials=TRIALS,
                  rows=rows, physical_selection=None, physical_acceptance=False)
    report["evaluation_id"] = digest(report)
    return report


def markdown(data):
    lines = [
        "# Compare straight viaduct spans and supports",
        "",
        "Compare the issued 10 m box with independently sized U-girders and a two-piece box under the same route, load and erection conditions. "
        "The earlier comparison kept one box and cage throughout. Its approximate $118m direct saving and $7,975 per 20 m placement headroom "
        "belong to the 148 km first programme. [Earlier common-section sensitivity](SPAN-COMPARISON.md)",
        "",
        f"This screen uses {data['route_km']:g} km of continuous double track, one straight run, "
        f"{data['axle_count']} axles and {data['passenger_train_kg']/1000:.2f} t at normal study crowd load. "
        "The shared running-line trial has 4.50 m track centres. Station islands require a different arrangement. "
        "End bents count once per continuous line. A partial end bay is budgeted as a whole placement. Its closure length and excess ordered length are reported separately and the closure design and price remain open.",
        "",
        "### Which design to quote",
        "",
        f"{data['passing_trial_count']} of {len(data['rows'])} trials pass the stated checks at {data['soil_kpa']} kPa and a "
        f"{data['crane_limit_t_at_12m']} t maximum working load at 12 m radius. "
        "Each price case identifies the lowest estimated 30-year present value among the passing trials. "
        "A supplier return and independent design review are still required.",
        "",
        "| Rate case | Lowest 30-year cost among screened options | Installed $m/km | 30-year PV $m/km |",
        "|---|---|---:|---:|",
    ]
    for case, leader in data["quotation_leaders"].items():
        if leader:
            lines.append(f"| {case} | {leader['label']} | {leader['installed_usd']/data['route_km']/1e6:.2f} "
                         f"| {leader['lifecycle_pv_usd']/data['route_km']/1e6:.2f} |")
        else:
            lines.append(f"| {case} | No trial passes all checks | — | — |")
    lines.extend([
        "",
        "### Shallow foundation case",
        "",
        f"The following base-rate comparison assumes {data['soil_kpa']} kPa. Each single-track U has 3.60 m of nominal clear channel. "
        "Each standard depth and its 200 mm deeper counterpart were evaluated. The table gives the candidate with the lowest priced "
        "30-year present value among the two depths passing the listed stress and handling screens, separately for each pier arrangement. "
        "Where both depths fail, the table gives the trial with fewer failed checks, then the lower projected cost if tied. The JSON retains every depth and every failure. "
        "The two-piece option is a new post-tensioned box with a match-cast joint and a temporary tower at midspan.",
        "",
        "| Span and family | Depth m | Pier | Footing width m | Supports | Lift unit t | Strand count | Crane trial t at 12 m | Installed $m/km | 30-year PV $m/km | Extra $/placement to match 10 m¹ | Screen |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    chosen = {}
    for row in data["rows"]:
        key = (row["span_m"], row["section"]["shape"], row["shared_pier"])
        rank = (sum(not passed for passed in row["checks"].values()), row["priced_cases"]["base"]["lifecycle_pv_usd"])
        if key not in chosen or rank < chosen[key][0]:
            chosen[key] = (rank, row)
    n = data["route_km"]
    for _, row in chosen.values():
        a, s, costcase = row["actions"], row["section"], row["priced_cases"]["base"]
        reasons = {"lift_fibre_min": "lifting tension", "release_fibre_min": "transfer tension",
                   "independent_footings_clear": "footings touch or overlap",
                   "available_crane": "crane exceeds available capacity",
                   "full_length_standard_bays": "partial end bay"}
        failed = [reasons.get(k, k.replace("_", " ")) for k,v in row["checks"].items() if not v]
        lines.append(f"| {row['span_m']} m {s['shape']} | {s['depth_m']:.2f} | {'shared' if row['shared_pier'] else 'separate'} "
                     f"| {row['support']['footing_width_m']:.2f} | {row['supports']:,} | {a['handling_unit_t']:.1f} | {a['strand_count']} "
                     f"| {a['chart_class_t_at_12m']} | {costcase['installed_usd']/1e6/n:.2f} | {costcase['lifecycle_pv_usd']/1e6/n:.2f} "
                     f"| {row['base_installed_headroom_per_placement_usd']:+,.0f} | {', '.join(failed) or 'trial screens pass'} |")
    lines.extend([
        "",
        "¹ Positive headroom is the additional installed dollars this alternative can absorb per actual lifting placement before matching "
        "the independent 10 m box at the same length and rates. A negative number means it is already dearer. Complete installed prices remain open.",
        "",
        "### What changes the order",
        "",
        "These three design sensitivities show how soil and price uncertainty affect the installed subtotal. "
        "An asterisk marks a footing trial where the independent pads touch or overlap. The preceding table gives each design's failed checks.",
        "",
        "| Quotation case | Low / base / high installed $m/km | 150 / 200 / 250 kPa installed $m/km at base rates |",
        "|---|---:|---:|",
    ])
    for key in [(10, "issued-box", False), (20, "U", True), (25, "U", True)]:
        _, row = chosen[key]
        range_cost = " / ".join(f"{row['priced_cases'][case]['installed_usd']/n/1e6:.2f}" for case in CASES)
        range_soil = " / ".join(f"{row['soil_sensitivity'][str(k)]['installed_usd_per_km']/1e6:.2f}"
                                + ("" if row["soil_sensitivity"][str(k)]["independent_footings_clear"] else "∗")
                                for k in (150, 200, 250))
        lines.append(f"| {row['label']} | {range_cost} | {range_soil} |")
    lines.extend([
        "",
        "The U is wide enough for a preliminary body-clearance trial. Its floor, web thickness, depth, gross area, centroid and inertia vary by span. "
        "Each U span has a full-pretension trial and a 200 mm deeper staged version. The latter takes roughly 30% of the final strands for handling, with 0.08L pickup inset, then adds profiled post-tensioning after landing. Extra ducts, anchors and stressing are priced. Stock stress is checked at pickup, midspan and on landing with the initial strands. Duct drape, end anchorage and losses need a supplier design. Prestress uses the issued strand's initial force "
        "and 30% loss, with zero bottom tension at peak positive service moment as a design target. The 10 m reference retains 12 strands. "
        "Hogging during the lift and full-transfer fibre stresses are separate screens. The deflection result bounds gross-section gravity curvature. "
        "Creep, cracking, camber, prestress transfer length, fatigue, local wheel load distribution and shear/torsion capacity require detailed design. "
        "The reported torque acts at the support pair. Open-section warping and lateral stability need shell analysis and a lifting trial. "
        "Check computed movement against rail, collector and boarding tolerances. This train uses a protected conductor and steel wheels.",
        "",
        "Two adjacent beam ends load an interior bent. The footing increases in 0.25 m width increments until vertical bearing and no-uplift trials "
        "pass for longitudinal braking and either one or both loaded tracks. Each cap extends at least 250 mm beyond the outer bearing pad. The common pier has a wider and deeper cap. "
        "Its one-sided train loads can govern the footing. Wind, seismic, piles, settlement, utilities, drainage, clearances and cap reinforcement "
        "need site-specific offers. Both foundations at the ends are conservatively priced as interior sizes.",
        "",
        "Each piece takes one haul and one lift. Hook demand includes 4 t rigging and a 1.10 handling multiplier. The 60, 110 and 180 t **working-load-at-radius** "
        "options are quotation hypotheses. Verify lift radius, temporary stability, slew, supporting pavement and travel. The segmented option pays for match casting, "
        "tensioning and tower cycles. Check the joint at full tendon force with the tower still engaged, then with the tower removed. "
        "A failed supported-joint stress check requires a redesigned tendon or a controlled, analysed unloading sequence. "
        "Lifting an unstressed half requires its own reinforcing and local pick design. "
        "The yard trial holds eight moulds, with 24 h and 48 h release cycles. Obtain occupation and capacity returns alongside the traffic closure bids.",
        "",
        "Prices use the repository's Iraqi cement, sand, gravel, reinforcing steel and currency inputs. Low/base/high rates cover ordinary civil scope, "
        "casting, haul, bearings, equipment, erection, disruption and support works. The other-elevated allowance is common per route-km. "
        "Trial moulds, strand rates, traffic bookings, maintenance and crane-class uplifts are estimating assumptions. The 30-year present value includes "
        "annual inspections and one bearing replacement at year 20 discounted at 4% real. Check contractor inclusion credits, abnormal haul limits, "
        "pile/special works, traffic staging, time-dependent PT maintenance and disruption before accepting a total. A low installed subtotal alone cannot select a design.",
        "",
        "Delhi Metro explicitly allows precast small U girders up to 30 m and describes two-crane erection and traffic constraints. "
        "Obtain local truck paths, lifting charts, designs and quotations for the same operating conditions. "
        f"[Delhi Metro civil construction specifications, section 10.1.1]({SOURCE_LINK})",
        "",
        "Run the same comparison for another route length, soil pressure, train or material from the repository root. "
        "The input hashes, study assumptions, envelopes, footprints, work quantities and low/base/high cost breakdowns are included in JSON.",
        "",
        "```sh",
        "python3 -m cities.Baghdad.engineering.mechanical.civil.family_comparison --check",
        "python3 -m cities.Baghdad.engineering.mechanical.civil.family_comparison --route-km 18 --soil-kpa 150 --crane-limit-t 60",
        "python3 -m cities.Baghdad.engineering.mechanical.civil.family_comparison --route-km 148.2 --soil-kpa 150 --json > build/span-families.json",
        "```",
        "",
        f"Evaluation `{data['evaluation_id']}`. All cases remain open for independent engineering review.",
    ])
    return "\n".join(lines)+"\n"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--route-km", default="12.0")
    p.add_argument("--soil-kpa", type=int, choices=(150,200,250), default=200)
    p.add_argument("--crane-limit-t", type=int, choices=(60,110,180), default=180,
                   help="maximum available working load in tonnes at a 12 m radius")
    p.add_argument("--cars", type=int, choices=(3,6), default=6)
    p.add_argument("--material", choices=vehicle.MATERIAL, default="steel")
    group = p.add_mutually_exclusive_group()
    for flag in ("--json","--check","--write"):
        group.add_argument(flag, action="store_true")
    args = p.parse_args()
    try:
        data = evaluate(args.route_km,args.cars,args.material,args.soil_kpa,args.crane_limit_t)
    except (InvalidOperation, ValueError) as error:
        p.error(str(error))
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True, allow_nan=False))
        return
    guide = markdown(data)
    path = HERE/"SPAN-FAMILIES.md"
    if args.check or args.write:
        if (data["route_km_decimal"],args.cars,args.material,args.soil_kpa,args.crane_limit_t) != ("12",6,"steel",200,180):
            p.error("The published guide uses the named reference inputs")
        if args.check and guide != path.read_text():
            raise ValueError("Rebuild SPAN-FAMILIES.md")
        if args.write:
            with disk_reservation(ROOT, HERE, "Viaduct family guide", 1 << 20):
                path.write_text(guide)
        print(data["evaluation_id"])
    else:
        print(guide)


if __name__ == "__main__":
    main()
