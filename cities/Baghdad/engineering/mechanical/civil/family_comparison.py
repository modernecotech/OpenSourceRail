"""Size and price straight, double-track viaduct options on one train load case."""
import argparse
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from hashlib import sha256
import json
from math import ceil, inf, isfinite, radians, sin
from pathlib import Path
from sys import float_info
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
PRICED_CRANE_CLASSES = (60, 110, 180)
PRICED_LIFT_RADIUS_M = 12.
TRIALS = {
    "track_pitch_m": 4.5, "braking_m_s2": 1., "grade_fraction": .02,
    "allowable_release_tension_mpa": 1.5, "allowable_release_compression_mpa": 18.,
    "rigging_t": 4., "lift_dynamic_factor": 1.10, "lift_radius_m": PRICED_LIFT_RADIUS_M,
    "cost_discount_real": .04, "rebar_kg_per_m3": 130., "strand_usd_kg": [1.3, 1.9, 3.1],
    "bearing_purchase_usd_each": [180., 450., 1400.], "closure_usd_shift": [500., 2400., 9500.],
    "annual_inspection_usd_bearing": [4., 12., 45.], "bearing_renewal_labour_usd": [250., 800., 2400.],
    "inspection_usd_span_year": [12., 40., 130.], "inspection_usd_pt_joint_year": [30., 100., 400.],
    "bed_and_form_usd": [75000., 160000., 360000.], "match_cast_joint_usd": [1900., 5800., 17000.],
    "staged_pt_per_girder_usd": [1300., 3300., 8600.], "duct_grout_stressing_usd_per_strand_m": [.9, 1.8, 4.2],
    "temporary_tower_cycle_usd": [1600., 5000., 16000.], "material_delivery_multiplier": [1.0, 1.25, 1.65],
}
SOURCE_LINK = "https://backend.delhimetrorail.com/documents/8790/OUTLINE_CONSTRUCTION_SPECIFICATIONS_for_Civil_Works_Revision-R4_June_2025.pdf"
AUDIT_CASES = ("central", "high")
LIFT_HEAVY_SIDE_SHARE = .60
AUDIT_HOLDS = [
    "Establish applicable combinations and limits for ultimate flexure, shear/torsion, fatigue, derailment, seismic, wind and thermal movements.",
    "Measure axle weights, dynamic wheel loads and braking distribution. Validate rail-seat and bearing load paths, track twist, camber and clearances.",
    "Measure concrete strength at release and lifting, modulus and losses. Check local transfer, tendon anchorage, cracking, temporary bracing and lifting inserts.",
    "Survey utilities, boreholes, water table, flood/scour and drainage. Verify settlement, foundation resistance and adjacent asset movements.",
    "Obtain transport axle loads, route swept paths, staged stability method, signed crane chart and independent design and construction approval.",
]


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


def engineering(length, sec, axle_actions, cage, cfg, *, strands_override=None):
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
    if strands_override is not None:
        strands = strands_override
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
    chart = next((t for t in PRICED_CRANE_CLASSES if charged_lift <= t), None)
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
                  positive_bearing_reactions=min_bearing > 0)
    actions = dict(moment_knm=moment, dead_moment_knm=dead_m, peak_track_reaction_kn=reaction,
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
    if strands_override is not None:
        factor = box["moving_load_factor"]
        hogging = factor*live["min_moment"]["value"]
        # The moving-load negative envelope occurs at the seated overhangs.
        # Use zero eccentricity at the seat, retaining the early straight
        # strands' eccentricity in the staged trial.
        end_eccentricity = e*early_strands/strands if sec["shape"] == "U" else 0.
        stiff = box["concrete_elastic_modulus_gpa"]*1e6*inertia
        actions.update(
            live_hogging_moment_knm=hogging,
            live_hogging_end_fibre_compression_mpa=fibres(installed*(1-loss), hogging, end_eccentricity),
            live_gravity_deflection_bound_mm=factor*live["max_moment"]["value"]*span**2/(8*stiff)*1000,
            lift_line_reactions_kn=[TRIALS["lift_dynamic_factor"]*r for r in (left_reaction,right_reaction)],
        )
    return actions


def erection_and_interfaces(actions, sec, cfg):
    box = cfg["box"]
    side = actions["bearing_offset_m"]
    reactions = actions["lift_line_reactions_kn"]
    heavy = LIFT_HEAVY_SIDE_SHARE*max(reactions)
    light = (1-LIFT_HEAVY_SIDE_SHARE)*max(reactions)
    angle = box["sling_angle_above_horizontal_deg"]
    thickness = sec["web_m"]
    floor = sec["floor_m"]
    median_width = sec["width_m"]-thickness
    if sec["shape"] == "U":
        torsion_j = (median_width*floor**3+2*(sec["depth_m"]-floor/2)*thickness**3)/3
        shear_flow = None
    else:
        median_depth = sec["depth_m"]-floor
        cell_area = median_width*median_depth
        torsion_j = 4*cell_area**2/(2*median_width/floor+2*median_depth/thickness)
        shear_flow = actions["end_torque_knm"]/(2*cell_area)
    return dict(
        assumed_lift_pad_half_spacing_m=side, trial_heavy_side_share=LIFT_HEAVY_SIDE_SHARE,
        sling_angle_above_horizontal_deg=angle, worst_vertical_load_heavy_light_leg_kn=[heavy, light],
        worst_sling_leg_tension_kn=heavy/sin(radians(angle)), asymmetric_pick_line_twist_knm=(heavy-light)*side,
        estimated_gross_st_venant_j_m4=torsion_j, closed_cell_end_shear_flow_kn_m=shear_flow,
        rail_vertical_load_motion_bound_mm=actions["live_gravity_deflection_bound_mm"],
        rail_twist_mm=None, rail_alignment_budget_mm=None, magnetic_gap_applicable=False,
        magnetic_gap_mm=None, deformation_hold="Wheel-supported span. Track and power-interface clearances require coupled rail, bearing, pier and foundation movements.",
    )


def support(a, shared, soil, cfg, *, fixed_footing_width_m=None):
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
    resolved = False
    widths = (fixed_footing_width_m,) if fixed_footing_width_m is not None else (i*.25 for i in range(10, 101))
    for side in widths:
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
            resolved = True
            break
    lateral_footing_gap = pitch-side if resolved and not shared else None
    return dict(footing_width_m=side if resolved else None, footing_depth_m=depth if resolved else None,
                concrete_m3=sub+footing if resolved else None,
                foundation_hold=None if resolved else "No shallow trial in the 2.5–25 m family satisfies the soil case. Price a site-specific foundation.",
                cap_cross_track_m=cap_length, cap_along_track_m=cap_width, cap_depth_m=cap_depth,
                cap_outer_pad_edge_margin_m=(track_head-2*a["bearing_offset_m"]-cfg["box"]["pad_width_m"])/2,
                footing_clear_gap_m=lateral_footing_gap, independent_footings_clear=(shared or lateral_footing_gap > 0) if resolved else None,
                peak_soil_kpa=max(pressures) if resolved else None, minimum_soil_kpa=min(pressures) if resolved else None,
                full_bent_longitudinal_braking_kn=live*tracks*horizontal_ratio,
                full_bent_bound_end_twist_knm=2*tracks*abs(a["end_torque_knm"]),
                crosshead_cantilever_knm=(dead+live)*pitch/2+2*abs(a["end_torque_knm"]) if shared else None)


def train_actions(record, bogie, service, cfg, cars, material, cases, high_train_mass_kg):
    loads, moving = {}, {}
    for name in cases:
        load = vehicle.load_case(record, bogie, service, cars, material, name)
        mass = load["loaded_train_kg"]
        if name == "high" and high_train_mass_kg is not None:
            if not isfinite(high_train_mass_kg) or high_train_mass_kg < loads["central"]["loaded_train_kg"]:
                raise ValueError("High train mass must be finite and at least the central mass")
            mass = high_train_mass_kg
        scale = mass/load["loaded_train_kg"]
        g = cfg["materials"]["gravity_m_s2"]
        axles = [(f"C{i+1}-A{j+1}", cx+dx, kg*scale*g/1000)
                 for i, cx in enumerate(record["interfaces"]["formation_body_from_car_x_m"][:cars])
                 for j, (dx, kg) in enumerate(zip(record["interfaces"]["body_from_axle_x_m"], load["axle_kg_per_car"]))]
        moving[name] = {length: moving_span(axles, length-.5, .25) for length in SPAN_OPTIONS}
        if len(cases) > 1:
            curve = []
            for length in SPAN_OPTIONS:
                # Occupied deck envelope, without the vertical dynamic multiplier.
                brake = (TRIALS["braking_m_s2"]/g + TRIALS["grade_fraction"])*max(
                    sum(force for _, x, force in axles if left <= x <= left+length) for _, left, _ in axles
                )
                moving[name][length]["full_stock_braking_kn"] = brake
                curve.append([length, brake])
            loads[name] = dict(loaded_train_kg=mass, axle_kg_per_car=[kg*scale for kg in load["axle_kg_per_car"]],
                               axle_loads=[dict(id=i, x_m=x, force_kn=f) for i,x,f in axles],
                               axle_mass_balance_kg=sum(f*1000/g for _,_,f in axles)-mass,
                               whole_train_braking_kn=mass*(TRIALS["braking_m_s2"]+g*TRIALS["grade_fraction"])/1000,
                               vehicle_load_state=name, load_scale=scale, full_stock_braking_by_span_kn=curve)
        else:
            loads[name] = load
    return loads, moving


def validate_offer(offer):
    fields = {"supplier", "offer_id", "physical_id", "placements", "lift_radius_m", "working_load_t",
              "haul_usd_per_placement", "erection_usd_per_placement", "placements_per_shift"}
    if not isinstance(offer, dict) or offer.keys() != fields:
        raise ValueError(f"Erection offer requires these fields: {', '.join(sorted(fields))}")
    if any(not isinstance(offer[k], str) or not offer[k].strip() for k in ("supplier", "offer_id", "physical_id")):
        raise ValueError("Identify the supplier, offer and physical trial")
    if len(offer["physical_id"]) != 64 or any(c not in "0123456789abcdef" for c in offer["physical_id"]):
        raise ValueError("Use the trial's full SHA-256 physical_id")
    if type(offer["placements"]) is not int or offer["placements"] <= 0:
        raise ValueError("Quote a positive whole number of placements")
    for key in fields-{"supplier", "offer_id", "physical_id", "placements"}:
        value = offer[key]
        if type(value) not in (float, int) or not isfinite(value) or value < 0 or (value == 0 and not key.endswith("_per_placement")):
            raise ValueError(f"Invalid quantity in erection offer: {key}")


def cost(row, rates, shop, basket, offers):
    n, p, bears, placements = (row[k] for k in ("beams", "supports", "bearings", "placements"))
    a, sec, base = row["actions"], row["section"], row["support"]
    chart_class = row["matched_crane_price_class_t"]
    length = row["span_m"]
    options = {}
    for i, name in enumerate(CASES):
        # Material allowances bought separately from fabrication, site works and haul labour.
        support_volume = p*base["concrete_m3"] if base["concrete_m3"] is not None else None
        vol = n*sec["volume_m3"]+(support_volume or 0)
        if sec["shape"] == "issued-box":
            beam_steel = row["counted_bar_kg_per_beam"]
        else:
            # Budget includes extra cage steel for links; supplier must return a cage schedule.
            beam_steel = sec["volume_m3"]*TRIALS["rebar_kg_per_m3"] + a["shear_links_demand_mm2_per_m"]*1e-6*7850*length*sec["depth_m"]
        steel = n*beam_steel+(support_volume or 0)*rates["rebar_t_per_m3"][i]*1000
        strand_kg = n*a["strand_count"]*length*row["strand_kg_m"]
        yard_size = min(8, placements)
        # Labour and yard handling estimated against issue's first 10m delivery allowance,
        # less its stated modelled standard haul. Variants scale with casting and set-ups.
        haul_rate = shop["civil-haul"]["usd"][i]
        fabrication = (rates["beam_fabrication_and_delivery_usd_each"][i]-haul_rate) * (
            .50*placements+.50*n*sec["volume_m3"]/13.404)
        overhead = rates["other_civil_usd_m_per_route_km"][i]*1e6*row["route_km"]
        parts = dict(materials=vol*basket["concrete"]*TRIALS["material_delivery_multiplier"][i]
                     +steel*basket["bar"]/1000 + strand_kg*TRIALS["strand_usd_kg"][i],
                     fabrication=fabrication,
                     bearing_supply_and_install=bears*(TRIALS["bearing_purchase_usd_each"][i]+shop["civil-bearing"]["usd"][i]),
                     forms=yard_size*TRIALS["bed_and_form_usd"][i]*(length/a["segments"]/10)**.8,
                     common_elevated_scope=overhead)
        missing = []
        if support_volume is None:
            missing.append("site foundation, associated materials and support works")
        else:
            parts["supports"] = p*rates["support_works_usd_each"][i]*(1.25 if row["shared_pier"] else 1.)
        closure_rate = TRIALS["closure_usd_shift"][i]
        logistics = []
        for offer in offers:
            shifts = ceil(Fraction(placements)/Fraction(str(offer["placements_per_shift"])))
            amounts = dict(haul=placements*offer["haul_usd_per_placement"],
                           erection=placements*offer["erection_usd_per_placement"], road_occupation=shifts*closure_rate)
            logistics.append((sum(amounts.values()), offer["offer_id"], offer["placements_per_shift"], shifts, amounts))
        if logistics:
            _, offer_id, productivity, shifts, amounts = min(logistics)
            source = "contractor offer"
            parts.update(amounts)
        elif chart_class is not None:
            factor = {60: 1., 110: 1.65, 180: 2.8}[chart_class]
            productivity = {60: 8, 110: 4, 180: 2}[chart_class]
            shifts = -(-placements // productivity)
            offer_id, source = None, "12 m planning rate"
            parts.update(haul=placements*haul_rate*factor, erection=placements*rates["lift_usd_each"][i]*factor,
                         road_occupation=shifts*closure_rate)
        else:
            missing.extend(("haul", "erection", "road occupation"))
            offer_id, source, productivity, shifts = None, "unpriced", None, None
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
        options[name] = dict(installed_usd=None if missing else installed, annual_inspection_usd=annual,
                             known_installed_subtotal_usd=installed, missing_cost_scope=missing, year20_bearings_usd=renew,
                             lifecycle_pv_usd=None if missing else pv, installed_breakdown_usd=parts,
                             logistics_source=source, offer_id=offer_id, placements_per_shift=productivity,
                             traffic_shifts=shifts)
    return options


def evaluate(route_km=12., cars=6, material="steel", soil_kpa=200, crane_limit_t=None,
             lift_radius_m=PRICED_LIFT_RADIUS_M, erection_offers=(), *, load_audit=False,
             high_train_mass_kg=None, selected_family=None, selected_span_m=None):
    erection_offers = list(erection_offers)
    for offer in erection_offers:
        validate_offer(offer)
    if len({o["offer_id"] for o in erection_offers}) != len(erection_offers):
        raise ValueError("Use distinct offer IDs for different erection returns")
    erection_offers.sort(key=lambda o: o["offer_id"])
    offer_status = {o["offer_id"]: "physical ID outside current study" for o in erection_offers}
    if not isfinite(lift_radius_m) or lift_radius_m <= 0:
        raise ValueError("Lift radius must be finite and positive in metres")
    if crane_limit_t is not None and (not isfinite(crane_limit_t) or crane_limit_t <= 0):
        raise ValueError("Available working load at the stated radius must be a finite positive number of tonnes")
    route_decimal = Decimal(str(route_km))
    if not route_decimal.is_finite() or route_decimal <= 0 or abs(route_decimal.adjusted()) > float_info.max_10_exp-9:
        raise ValueError("Route length must be positive and leave nine decimal orders of float range for total and per-km costs")
    if cars not in (3, 6) or material not in vehicle.MATERIAL:
        raise ValueError("Choose an evaluated 3- or 6-car load and supported body material")
    try:
        soil_kpa = float(soil_kpa)
    except OverflowError as error:
        raise ValueError("Representative soil bearing pressure exceeds the numerical range") from error
    if not isfinite(soil_kpa) or soil_kpa <= 0:
        raise ValueError("Representative soil bearing pressure must be finite and positive")
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
    states = AUDIT_CASES if load_audit else ("central",)
    loads, moving = train_actions(record, bogie, sys["service_power"], cfg, cars, material, states, high_train_mass_kg)
    designs = [("issued-box", 10, 0)] + [("U", l, d) for l in SPAN_OPTIONS for d in (0, .20)]
    designs += [("joined-box", 20, 0), ("joined-box", 20, .20)]
    if load_audit and (selected_family is not None or selected_span_m is not None):
        designs = [(family, length, depth) for family, length, depth in designs
                   if (selected_family is None or family == selected_family)
                   and (selected_span_m is None or length == selected_span_m)]
        if not designs:
            raise ValueError("No trial in the specified beam family and span")
    rows = []
    for kind, length, extra in designs:
        sec = section(kind, length, extra, cfg["box"])
        governing_bending = max(states, key=lambda name: moving[name][length]["max_moment"]["value"])
        a = engineering(length, sec, moving[governing_bending], cage, cfg)
        if load_audit:
            initial_strands = a["strand_count"]
            cases_by_load = {name: engineering(length, sec, moving[name], cage, cfg, strands_override=initial_strands)
                             for name in states}
            a = dict(cases_by_load[governing_bending], shear_links_demand_mm2_per_m=max(
                actions["shear_links_demand_mm2_per_m"] for actions in cases_by_load.values()
            ))
            governing_support = max(states, key=lambda name: cases_by_load[name]["dynamic_live_reaction_kn"])
            support_actions = cases_by_load[governing_support]
            erection = erection_and_interfaces(a, sec, cfg)
            for actions in cases_by_load.values():
                actions["checks"]["positive_lifting_reactions"] = min(actions["lift_line_reactions_kn"]) > 0
        else:
            support_actions = a
        full_bays, closure = divmod(route_m, length)
        bays = full_bays + bool(closure)
        for shared in (False, True):
            base = support(support_actions, shared, soil_kpa, cfg)
            piers = (bays+1)*(1 if shared else 2)
            segments = a["segments"]
            row = dict(label=f"{length}m {kind} {sec['depth_m']:.2f}m / {'shared' if shared else 'separate'}",
                       span_m=length, section=sec, shared_pier=shared, route_km=route_km, actions=a, support=base,
                       beams=2*bays, supports=piers, bearings=8*bays, placements=2*bays*segments,
                       strand_kg_m=cage["strand"]["catalogue_linear_mass_kg_m"],
                       counted_bar_kg_per_beam=cage["straight_and_developed_bar_kg"] if kind == "issued-box" else None)
            row["closure_bay_m"] = float(closure) if closure else None
            row["ordered_excess_length_per_track_m"] = float(bays*length-route_m)
            row["checks"] = dict(a["checks"], full_length_standard_bays=closure == 0)
            if base["independent_footings_clear"] is not None:
                row["checks"]["independent_footings_clear"] = base["independent_footings_clear"]
            if crane_limit_t is not None:
                row["checks"]["available_crane"] = a["chart_demand_t"] <= crane_limit_t
            if load_audit:
                row["governing_bending_load"] = governing_bending
                row["governing_bent_load"] = governing_support
                row["load_case_train_kg"] = {name: loads[name]["loaded_train_kg"] for name in states}
                row["load_case_actions"] = cases_by_load
                row["load_case_fixed_footing_checks"] = {
                    name: support(actions, shared, soil_kpa, cfg, fixed_footing_width_m=base["footing_width_m"])
                    for name, actions in cases_by_load.items()
                } if base["footing_width_m"] is not None else dict.fromkeys(states)
                row["checks"].update({
                    f"{name}.{key}": passed for name, actions in cases_by_load.items()
                    for key, passed in actions["checks"].items()
                })
                row["checks"]["foundation_for_load_envelope"] = all(
                    result is not None and not result["foundation_hold"]
                    for result in row["load_case_fixed_footing_checks"].values()
                )
                row["erection_and_interfaces"] = erection
                row["full_standard_bays"] = full_bays
                row["end_closure_design_hold"] = "Site-specific end bay geometry and price required." if closure else None
                standard_supports = (full_bays+1)*(1 if shared else 2)
                beam_bar = row["counted_bar_kg_per_beam"] if kind == "issued-box" else (
                    sec["volume_m3"]*TRIALS["rebar_kg_per_m3"]
                    + a["shear_links_demand_mm2_per_m"]*1e-6*7850*length*sec["depth_m"]
                )
                row["quantities"] = dict(
                    equivalent_beam_concrete_m3=row["beams"]*sec["volume_m3"],
                    full_standard_beam_concrete_m3=2*full_bays*sec["volume_m3"],
                    equivalent_beam_concrete_mass_t=row["beams"]*a["mass_t"],
                    foundation_and_support_concrete_m3=piers*base["concrete_m3"] if base["concrete_m3"] is not None else None,
                    two_track_metres=2*float(route_m), transfer_and_erection_units=row["placements"],
                    standard_beams=2*full_bays, standard_supports=standard_supports, standard_bearings=8*full_bays,
                    standard_placements=2*full_bays*segments, standard_beam_bar_planning_kg=2*full_bays*beam_bar,
                    standard_beam_strand_kg=2*full_bays*a["strand_count"]*length*row["strand_kg_m"],
                    standard_support_concrete_m3=standard_supports*base["concrete_m3"] if base["concrete_m3"] is not None else None,
                )
            matched_class = a["chart_class_t_at_12m"] if lift_radius_m == PRICED_LIFT_RADIUS_M else None
            row["matched_crane_price_class_t"] = matched_class
            row["haul_trips"] = row["placements"]
            row["mould_positions"] = min(8,row["placements"])
            row["casting_days_at_24h_cycle"] = -(-row["placements"] // row["mould_positions"])
            row["casting_days_at_48h_cycle"] = 2*row["casting_days_at_24h_cycle"]
            row["source_train_candidate_id"] = record["candidate_id"]
            row["physical_id"] = digest(dict(section=sec, length=length, strands=a["strand_count"], strand_e=a["tendon_eccentricity_m"],
                                              footing=[base["footing_width_m"], base["footing_depth_m"]],
                                              crosshead=[base["cap_cross_track_m"], base["cap_along_track_m"], base["cap_depth_m"]],
                                              shared=shared, pier_height=cfg["pier"]["column_height_m"],
                                              tracks_pitch=TRIALS["track_pitch_m"], segments=segments, source_cage=cage["physical_id"]))
            matching = []
            for offer in erection_offers:
                if offer["physical_id"] != row["physical_id"]:
                    continue
                if offer["lift_radius_m"] != lift_radius_m:
                    status = "different lift radius"
                elif offer["placements"] != row["placements"]:
                    status = "different order quantity"
                elif offer["working_load_t"] < a["chart_demand_t"]:
                    status = "offered working load below hook demand"
                else:
                    status = "matched"
                    matching.append(offer)
                offer_status[offer["offer_id"]] = status
            cases = cost(row, rates, shop, basket, matching)
            row["priced_cases"] = {k: v for k, v in cases.items() if v["installed_usd"] is not None}
            row["partial_cost_cases"] = {k: v for k, v in cases.items() if v["installed_usd"] is None}
            if load_audit:
                row["standard_only_cost_cases"] = cases if not closure else None
                if closure and full_bays:
                    standard = dict(row, route_km=full_bays*length/1000, beams=2*full_bays,
                                    supports=standard_supports, bearings=8*full_bays, placements=2*full_bays*segments)
                    # The scoped contractor quote is for the complete order.
                    # A separate standard-only procurement schedule needs its own return.
                    row["standard_only_cost_cases"] = cost(standard, rates, shop, basket, [])
            row["placements_per_shift"] = cases["base"]["placements_per_shift"]
            row["traffic_shifts"] = cases["base"]["traffic_shifts"]
            row["pricing_hold"] = base["foundation_hold"] or (None if row["priced_cases"] else
                                      f"Request crane, haul and erection rates for the {lift_radius_m:g} m lift")
            row["soil_sensitivity"] = {}
            for soil in (150, 200, 250):
                alt_support = support(support_actions, shared, soil, cfg)
                # The quote identifies the whole physical trial, including the footing dimensions.
                same_geometry = all(alt_support[k] == base[k] for k in ("footing_width_m", "footing_depth_m"))
                alt_cost = cost(dict(row, support=alt_support), rates, shop, basket, matching if same_geometry else [])["base"]
                row["soil_sensitivity"][str(soil)] = {
                    "foundation_hold": alt_support["foundation_hold"],
                    "footing_width_m": alt_support["footing_width_m"],
                    "footing_clear_gap_m": alt_support["footing_clear_gap_m"],
                    "independent_footings_clear": alt_support["independent_footings_clear"],
                    "installed_usd_per_km": alt_cost["installed_usd"]/route_km if alt_cost["installed_usd"] is not None else None,
                    "lifecycle_pv_usd_per_km": alt_cost["lifecycle_pv_usd"]/route_km if alt_cost["lifecycle_pv_usd"] is not None else None,
                }
            row["complete_installed_usd"] = None
            row["eligible_for_selection"] = False
            if load_audit:
                row["failed_checks"] = [name for name, passed in row["checks"].items()
                                        if not passed and name not in (*a["checks"], "full_length_standard_bays")]
                row["quotation_screen_passed"] = not row["failed_checks"] and not base["foundation_hold"]
                row["eligible_for_quotation"] = row["quotation_screen_passed"] and bool(row["priced_cases"])
            rows.append(row)
    reference = next((r for r in rows if r["section"]["shape"] == "issued-box" and not r["shared_pier"]), None)
    ref = reference["priced_cases"].get("base") if reference else None
    for row in rows:
        base = row["priced_cases"].get("base")
        row["base_installed_headroom_per_placement_usd"] = (ref["installed_usd"]-base["installed_usd"])/row["placements"] if base and ref else None
        row["base_pv_change_vs_reference_usd"] = base["lifecycle_pv_usd"]-ref["lifecycle_pv_usd"] if base and ref else None
        if load_audit:
            row["audit_row_id"] = digest(row)
    files = [Path(__file__), Path(vehicle.__file__), Path(__import__(moving_span.__module__, fromlist=["x"]).__file__),
             HERE/"concept.toml", CITY/"system.toml", CITY/"iraq-capital.toml", CITY/"airport-works.toml", CITY/"iraq-market.toml",
             vehicle.PROTOTYPE/"shop-rates.toml", vehicle.PROTOTYPE/"airport-prototype.zip"]
    sources = {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()).hexdigest() for p in files}
    screened = [r for r in rows if (r["quotation_screen_passed"] if load_audit else
                                    all(r["checks"].values()) and not r["support"]["foundation_hold"])]
    priced = [r for r in screened if r["priced_cases"]]
    quotations = {}
    for case in CASES:
        if priced:
            leader = min(priced, key=lambda r: r["priced_cases"][case]["lifecycle_pv_usd"])
            prices = leader["priced_cases"][case]
            quotations[case] = dict(label=leader["label"], physical_id=leader["physical_id"],
                                    installed_usd=prices["installed_usd"], lifecycle_pv_usd=prices["lifecycle_pv_usd"],
                                    logistics_source=prices["logistics_source"], offer_id=prices["offer_id"])
            if load_audit:
                quotations[case].update(closure_bay_m=leader["closure_bay_m"], modelled_standard_stock_budget=True)
        else:
            quotations[case] = None
    decimal_text = format(route_decimal, "f")
    report = dict(schema="viaduct-family-comparison/1", route_km=route_km,
                  route_km_decimal=decimal_text.rstrip("0").rstrip(".") if "." in decimal_text else decimal_text,
                  cars=cars, material=material, soil_kpa=soil_kpa, crane_limit_t=crane_limit_t,
                  crane_limit_t_at_12m=crane_limit_t if lift_radius_m == PRICED_LIFT_RADIUS_M else None,
                  lift_radius_m=lift_radius_m, priced_lift_radius_m=PRICED_LIFT_RADIUS_M,
                  erection_offers=[dict(offer=o, sha256=digest(o), status=offer_status[o["offer_id"]]) for o in erection_offers],
                  passing_trial_count=len(screened), priced_passing_trial_count=len(priced),
                  unresolved_foundation_count=sum(bool(r["support"]["foundation_hold"]) for r in rows),
                  priced_trial_count=sum(bool(r["priced_cases"]) for r in rows), quotation_leaders=quotations,
                  passenger_train_kg=loads["central"]["loaded_train_kg"], axle_count=4*cars, member_sources=sources,
                  trials=dict(TRIALS, lift_radius_m=lift_radius_m),
                  rows=rows, physical_selection=None, physical_acceptance=False)
    if load_audit:
        report.update(schema="viaduct-high-load-audit/1", load_cases=loads,
                      source_train_candidate_id=record["candidate_id"], source_train_evaluation_id=record["evaluation_id"],
                      source_cage_physical_id=cage["physical_id"],
                      selected_family=selected_family, selected_span_m=selected_span_m,
                      service_moving_load_factor=cfg["box"]["moving_load_factor"],
                      acceptance_holds=AUDIT_HOLDS,
                      pricing_scope="Comparative straight double-track stock and support budget. A partial bay carries a full standard-stock allowance; closure design and actual price remain open. Station, vehicle, power equipment, land and network costs require their own ledger.",
                      load_case_limitations="Unequal point axle loads on a simply supported beam. The quoted dynamic multiplier, lateral eccentricity, lift imbalance, shallow bearing pressure and section properties are planning hypotheses.",
                      calculation_sources={"moving_load": "prototype/weights.py:moving_span", "axles": "simulation/vehicle_civil.py:load_case",
                                           "materials": "mechanical/civil/concept.toml", "rate_registers": ["iraq-capital.toml", "airport-works.toml", "iraq-market.toml", "engineering/prototype/shop-rates.toml"],
                                           "erection_precedent": SOURCE_LINK})
        report["input_id"] = digest(dict(route_km=report["route_km_decimal"], soil_kpa=soil_kpa, cars=cars,
                                         material=material, limits=[crane_limit_t,lift_radius_m], erection_offers=erection_offers,
                                         requested_mass_kg=high_train_mass_kg, load_cases=loads, family=selected_family, span_m=selected_span_m,
                                         trials=report["trials"], dynamic_factor=report["service_moving_load_factor"],
                                         lift_heavy_side_share=LIFT_HEAVY_SIDE_SHARE))
    report["evaluation_id"] = digest(report)
    return report


def evaluate_high_load(route_km=12., cars=6, material="steel", soil_kpa=200, crane_limit_t=None,
                       lift_radius_m=PRICED_LIFT_RADIUS_M, erection_offers=(), high_train_mass_kg=None,
                       selected_family=None, selected_span_m=None):
    """Compare fixed physical trials carrying both central and high train loads."""
    return evaluate(route_km, cars, material, soil_kpa, crane_limit_t, lift_radius_m, erection_offers,
                    load_audit=True, high_train_mass_kg=high_train_mass_kg,
                    selected_family=selected_family, selected_span_m=selected_span_m)


def markdown(data):
    capacity = data["crane_limit_t"]
    radius = data["lift_radius_m"]
    example = next(r for r in data["rows"] if r["span_m"] == 20 and r["section"]["staged_post_tension"] and r["shared_pier"])
    capacity_text = (f"The user supplied {capacity:g} t of available capacity at {radius:g} m radius."
                     if capacity is not None else f"No common site rating was entered at {radius:g} m. Each contractor offer is checked against its stated working load.")
    if radius != data["priced_lift_radius_m"]:
        capacity_text += f" The planning rates cover {data['priced_lift_radius_m']:g} m. Only matched contractor offers price the {radius:g} m lift."
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
        f"{len(data['rows'])} trials were investigated at {data['soil_kpa']:g} kPa. {data['unresolved_foundation_count']} require a foundation outside the modeled family. "
        f"{data['priced_trial_count']} have a priced civil subtotal, "
        f"{data['passing_trial_count']} pass the stated checks, and {data['priced_passing_trial_count']} satisfy both conditions. {capacity_text} "
        "Each price case identifies the lowest estimated 30-year present value among trials that pass and carry a price. "
        "Confirm supplier scope, the load chart and independent design review before procurement.",
        "",
        "| Rate case | Lowest 30-year cost among screened options | Installed $m/km | 30-year PV $m/km | Haul and erection rates |",
        "|---|---|---:|---:|---|",
    ]
    for case, leader in data["quotation_leaders"].items():
        if leader:
            lines.append(f"| {case} | {leader['label']} | {leader['installed_usd']/data['route_km']/1e6:.2f} "
                         f"| {leader['lifecycle_pv_usd']/data['route_km']/1e6:.2f} | {leader['offer_id'] or leader['logistics_source']} |")
        else:
            reason = "Passing trials need an erection quote" if data["passing_trial_count"] else "No trial passes all checks"
            if data["unresolved_foundation_count"] and not data["passing_trial_count"]:
                reason = "No priced, passing trial. Site foundation design required."
            lines.append(f"| {case} | {reason} | — | — | — |")
    lines.extend([
        "",
        "### Shallow foundation case",
        "",
        f"The following base-rate comparison assumes {data['soil_kpa']:g} kPa. Each single-track U has 3.60 m of nominal clear channel. "
        "Each standard depth and its 200 mm deeper counterpart were evaluated. The table gives the candidate with the lowest priced "
        "30-year present value among the two depths passing the listed stress and handling screens, separately for each pier arrangement. "
        "Where neither depth passes, the table gives priority to a modeled foundation, then fewer failed checks and the lower projected cost if tied. The JSON retains every depth and every failure. "
        "The two-piece option is a new post-tensioned box with a match-cast joint and a temporary tower at midspan.",
        "",
        f"| Span and family | Depth m | Pier | Footing width m | Supports | Lift unit t | Strand count | Hook demand / matched price band t at {radius:g} m | Installed $m/km | 30-year PV $m/km | Extra $/placement to match 10 m¹ | Screen |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ])
    chosen = {}
    for row in data["rows"]:
        key = (row["span_m"], row["section"]["shape"], row["shared_pier"])
        rank = (bool(row["support"]["foundation_hold"]), sum(not passed for passed in row["checks"].values()),
                row["priced_cases"].get("base", {}).get("lifecycle_pv_usd", inf))
        if key not in chosen or rank < chosen[key][0]:
            chosen[key] = (rank, row)
    n = data["route_km"]
    for _, row in chosen.values():
        a, s, costcase = row["actions"], row["section"], row["priced_cases"].get("base")
        prices = (f"{costcase['installed_usd']/1e6/n:.2f} | {costcase['lifecycle_pv_usd']/1e6/n:.2f}"
                  if costcase else f"{row['partial_cost_cases']['base']['known_installed_subtotal_usd']/1e6/n:.2f} partial | —")
        margin = row["base_installed_headroom_per_placement_usd"]
        extra = f"{margin:+,.0f}" if margin is not None else "—"
        reasons = {"lift_fibre_min": "lifting tension", "release_fibre_min": "transfer tension",
                   "independent_footings_clear": "footings touch or overlap",
                   "available_crane": "crane exceeds available capacity",
                   "full_length_standard_bays": "partial end bay"}
        failed = [reasons.get(k, k.replace("_", " ")) for k,v in row["checks"].items() if not v]
        if row["support"]["foundation_hold"]:
            failed.append("foundation unresolved")
        width = row["support"]["footing_width_m"]
        footing_text = f"{width:.2f}" if width is not None else "unknown"
        matched = costcase["offer_id"] if costcase and costcase["offer_id"] else row["matched_crane_price_class_t"] or "unpriced"
        lines.append(f"| {row['span_m']} m {s['shape']} | {s['depth_m']:.2f} | {'shared' if row['shared_pier'] else 'separate'} "
                     f"| {footing_text} | {row['supports']:,} | {a['handling_unit_t']:.1f} | {a['strand_count']} "
                     f"| {a['chart_demand_t']:.1f} / {matched} | {prices} "
                     f"| {extra} | {', '.join(failed) or 'trial screens pass'} |")
    lines.extend([
        "",
        "¹ Positive headroom is the additional installed dollars this alternative can absorb per actual lifting placement before matching "
        "the independent 10 m box at the same length and rates. A negative number means it is already dearer. Complete installed prices remain open.",
        "",
        "A partial figure includes only priced work. The JSON lists every included amount and the outstanding scope in `partial_cost_cases`. "
        "When the crane has no price, the material, casting, forms and modeled support costs remain visible. They do not enter the quotation ranking on their own.",
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
        range_cost = (" / ".join(f"{row['priced_cases'][case]['installed_usd']/n/1e6:.2f}" for case in CASES)
                      if row["priced_cases"] else "Quote required")
        soil_costs = []
        for sensitivity in row["soil_sensitivity"].values():
            price = sensitivity["installed_usd_per_km"]
            suffix = "∗" if sensitivity["independent_footings_clear"] is False else ""
            soil_costs.append(f"{price/1e6:.2f}{suffix}" if price is not None else "unpriced")
        range_soil = " / ".join(soil_costs)
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
        "Enter a positive site bearing pressure using `--soil-kpa`. The 150, 200 and 250 kPa comparisons remain visible. "
        "Two adjacent beam ends load an interior bent. The shallow trial evaluates square widths of 2.5–25 m in 0.25 m increments until vertical bearing and no-uplift trials "
        "pass for longitudinal braking and either one or both loaded tracks. Each cap extends at least 250 mm beyond the outer bearing pad. The common pier has a wider and deeper cap. "
        "Its one-sided train loads can govern the footing. Wind, seismic, piles, settlement, utilities, drainage, clearances and cap reinforcement "
        "need site-specific offers. Both foundations at the ends are conservatively priced as interior sizes.",
        "",
        "The 60 t figure originated as a provisional lifting assumption with no verified crane chart. "
        "[Original pilot lifting inputs](https://github.com/modernecotech/OpenSourceRail/blob/5ffe46dceb9e23db594fbe033c472fd847772969/engineering/pilot_civil/policy.json#L103-L110)",
        "",
        "Each piece takes one haul and one lift. Hook demand includes assumed 4 t rigging and a 1.10 handling multiplier. "
        "The 60, 110 and 180 t bands estimate costs at 12 m radius. A heavier lift requires a new price. "
        "Set `--lift-radius-m` to the surveyed radius and `--crane-limit-t` to the available working load at that radius. "
        "Changing radius changes the chart requirement and rate coverage. The suspended mass and rigging still determine hook demand. "
        "Verify the radius, rigging, ground bearing and lift method at the site. The segmented option pays for match casting, "
        "tensioning and tower cycles. Check the joint at full tendon force with the tower still engaged, then with the tower removed. "
        "A failed supported-joint stress check requires a redesigned tendon or a controlled, analysed unloading sequence. "
        "Lifting an unstressed half requires its own reinforcing and local pick design. "
        "The yard trial holds eight moulds, with 24 h and 48 h release cycles. Obtain occupation and capacity returns alongside the traffic closure bids.",
        "",
        "The 1.5 MPa release tension and 18 MPa release compression checks are provisional material targets. The three shallow soil pressures are hypotheses. "
        "Obtain release-strength data, surveyed soil and authority criteria before structural selection. "
        "Prices use the repository's Iraqi cement, sand, gravel, reinforcing steel and currency inputs. Low/base/high are estimate cases covering ordinary civil scope, "
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
        "python3 -m cities.Baghdad.engineering.mechanical.civil.family_comparison --lift-radius-m 18 --crane-limit-t 95.5",
        "python3 -m cities.Baghdad.engineering.mechanical.civil.family_comparison --route-km 148.2 --soil-kpa 150 --json > build/span-families.json",
        "```",
        "",
        "To enter a contractor return, copy the exact `physical_id` and `placements` from the relevant trial's JSON. This example uses the deeper 20 m U on a shared pier. "
        "The haul and erection rates are delivered USD per placement, exclusive of traffic closure. The working load must cover modeled hook demand at the quoted radius.",
        "",
        "```json",
        json.dumps(dict(supplier="Example contractor", offer_id="example-A",
            physical_id=example["physical_id"], placements=example["placements"],
            lift_radius_m=18, working_load_t=95.5, haul_usd_per_placement=1200, erection_usd_per_placement=3500,
            placements_per_shift=4), indent=2),
        "```",
        "",
        "Run the matching scope with `--lift-radius-m 18 --erection-offer offer.json`. Repeat `--erection-offer` for other bidders. "
        "Matched returns replace the planning haul and erection rates. For each rate case the model compares those offers including traffic closures at their respective production rates. "
        "Materials, the price per closure and other civil work retain their estimating basis. Each return has a digest and match status in JSON.",
        "",
        f"Evaluation `{data['evaluation_id']}`. All cases remain open for independent engineering review.",
    ])
    return "\n".join(lines)+"\n"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--route-km", default="12.0")
    p.add_argument("--soil-kpa", type=float, default=200, help="positive representative shallow bearing pressure in kPa")
    p.add_argument("--crane-limit-t", type=float,
                   help="available working load in tonnes at the entered radius, if known")
    p.add_argument("--lift-radius-m", type=float, default=PRICED_LIFT_RADIUS_M,
                   help="lift radius in metres; the existing rate register covers 12 m")
    p.add_argument("--erection-offer", action="append", type=Path, default=[],
                   help="scoped haul and erection offer JSON (repeat for multiple suppliers)")
    p.add_argument("--cars", type=int, choices=(3,6), default=6)
    p.add_argument("--material", choices=vehicle.MATERIAL, default="steel")
    p.add_argument("--high-load", action="store_true", help="audit the same physical trials at central and high axle loads in JSON")
    p.add_argument("--high-train-mass-kg", type=float)
    p.add_argument("--family", choices=("issued-box", "U", "joined-box"))
    p.add_argument("--span-m", type=int, choices=SPAN_OPTIONS)
    group = p.add_mutually_exclusive_group()
    for flag in ("--json","--check","--write"):
        group.add_argument(flag, action="store_true")
    args = p.parse_args()
    if args.high_load and not args.json:
        p.error("Use --json for the high-load audit")
    if not args.high_load and any(value is not None for value in (args.high_train_mass_kg, args.family, args.span_m)):
        p.error("High load options require --high-load")
    try:
        data = evaluate(args.route_km,args.cars,args.material,args.soil_kpa,args.crane_limit_t,args.lift_radius_m,
                        [json.loads(path.read_text()) for path in args.erection_offer],
                        load_audit=args.high_load, high_train_mass_kg=args.high_train_mass_kg,
                        selected_family=args.family, selected_span_m=args.span_m)
    except (InvalidOperation, ValueError, OSError) as error:
        p.error(str(error))
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True, allow_nan=False))
        return
    guide = markdown(data)
    path = HERE/"SPAN-FAMILIES.md"
    if args.check or args.write:
        if args.erection_offer or (data["route_km_decimal"],args.cars,args.material,args.soil_kpa,args.crane_limit_t,args.lift_radius_m) != ("12",6,"steel",200,None,PRICED_LIFT_RADIUS_M):
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
