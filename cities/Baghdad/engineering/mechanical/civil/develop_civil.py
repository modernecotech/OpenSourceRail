"""Geometry and preliminary elastic gravity action for one station bay and one track span."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import tomllib

DIR = Path(__file__).resolve().parent
PARENT = DIR.parent
CITY = PARENT.parents[1]


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(inputs):
    return hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()


def box_screen(box, mat, track, pier):
    length, span = track["beam_stock_length_m"], track["effective_span_m_hypothesis"]
    end = box["solid_end_m"]
    b, h, t, s = (box[k] for k in ("width_m", "depth_m", "web_m", "slab_m"))
    a, void = b * h, (b - 2*t) * (h - 2*s)
    area = a - void
    inertia = (b*h**3 - (b-2*t)*(h-2*s)**3)/12
    volume = area*length + 2*end*void
    inset = (length-span)/2
    seats = track["bearing_seat_xy_m_from_stock_end"]
    lateral = max(abs(y) for _, y in seats)
    pad_w, pad_l = box["pad_width_m"], box["pad_length_m"]
    if not (0 < pad_l/2 < inset < end-pad_l/2 and lateral + pad_w/2 <= b/2 and area > 0):
        raise ValueError("Bearing pad outside solid end zone")
    if not math.isclose(track["moving_gravity_only"]["stock_overhang_per_end_m"], inset):
        raise ValueError("Live load extent differs from beam stock")
    rho = mat["rc_unit_weight_kn_m3"]
    uniform = area*rho + box["superimposed_dead_kn_m"]
    dead_r = (uniform*length+2*end*void*rho)/2
    # Midspan moment from left reaction and all distributed weight left of midspan,
    # including the stock overhang and the extra concrete in the solid end.
    dead_m = dead_r*span/2 - uniform*length**2/8 - end*void*rho*(length-end)/2
    live = track["moving_gravity_only"]
    factor = box["moving_load_factor"]
    peak_r = factor*live["max_end_reaction_kn_sampled"]
    peak_m = factor*live["max_live_moment_knm_sampled"]
    twist = peak_r*box["live_lateral_eccentricity_m"]
    peak_pad = (dead_r+peak_r)/2 + twist/(2*lateral)
    section_modulus = 2*inertia/h
    positive_moment = dead_m+peak_m
    force_for_zero_bottom_stress = positive_moment/(section_modulus/area+box["effective_tendon_eccentricity_m"])
    pick = box["lift_pick_inset_m"]
    if not end < pick < length/2:
        raise ValueError("Pick station incompatible with solid end length")
    pick_negative_m = -(area*rho*pick**2/2 + end*void*rho*(pick-end/2))
    pick_positive_m = volume*rho/2*(length/2-pick) - area*rho*length**2/8 - end*void*rho*(length-end)/2
    footing_area = pier["footing_width_m"]**2
    column_stock = pier["column_width_m"]**2*pier["column_height_m"]
    cap_stock = pier["cap_width_m"]*pier["cap_length_m"]*pier["cap_depth_m"]
    footing_stock = footing_area*pier["footing_depth_m"]
    compression = 2*(dead_r+peak_r) + (column_stock+cap_stock+footing_stock)*rho
    supports = dict(column_volume_m3=column_stock, cap_volume_m3=cap_stock,
                    footing_volume_m3=footing_stock, concentric_vertical_load_upper_kn=compression,
                    uniform_soil_contact_pressure_kpa=compression/footing_area,
                    pressure_sensitivities=[{"assumed_soil_pressure_kpa":pressure,
                        "contact_minus_assumed_kpa":compression/footing_area-pressure}
                        for pressure in pier["soil_pressures_kpa"]])
    return dict(length_m=length, bearing_span_m=span, bearing_xy_m=seats,
                midspan_area_m2=area, midspan_I_m4=inertia, gross_concrete_m3=volume,
                reinforced_stock_weight_kn=volume*rho, equivalent_stock_t=volume*rho/mat["gravity_m_s2"],
                pad_count=len(seats), pad_end_margin_m=inset-pad_l/2,
                pad_side_margin_m=b/2-lateral-pad_w/2,
                dead_end_reaction_kn=dead_r, dead_midspan_moment_knm=dead_m,
                live_end_reaction_kn=peak_r, live_moment_knm=peak_m,
                positive_moment_upper_knm=dead_m+peak_m,
                elastic_flexural_stress_range_plus_minus_mpa=(dead_m+peak_m)*h/(2*inertia)/1000,
                bearing_pair_torsion_knm=twist, highest_pad_reaction_kn=peak_pad,
                pad_mean_pressure_mpa=peak_pad/(pad_w*pad_l)/1000,
                midspan_box_shear_flow_torsion_kn_m=twist/(2*(b-t)*(h-s)),
                centre_deflection_curvature_bound_mm=1000*span**2*positive_moment/(8*box["concrete_elastic_modulus_gpa"]*1e6*inertia),
                effective_axial_force_for_zero_bottom_stress_kn=force_for_zero_bottom_stress,
                stock_lift_hogging_knm=pick_negative_m, stock_lift_midspan_knm=pick_positive_m,
                vertical_load_per_pick_line_kn=volume*rho/2,
                sling_leg_kn_equal_four_point=volume*rho/(4*math.sin(math.radians(box["sling_angle_above_horizontal_deg"]))),
                pier_gravity_screen=supports)


def platform_screen(p, steel, mat, station, quotation):
    bay, width = quotation["deck_bay_m"], station["island_width_m"]
    n = p["panels_across"]
    length, breadth = bay-p["panel_joint_m"], width/n-p["panel_joint_m"]
    depth = p["panel_thickness_m"]
    span = bay-2*p["seat_centre_from_bent_m"]
    rho = mat["rc_unit_weight_kn_m3"]
    volume = length*breadth*depth
    # Finishes and crowd use the full tributary width, including the joint.
    dead = breadth*depth*rho + width/n*p["surface_services_kn_m2"]
    live = width/n*p["crowd_kn_m2"]
    q = dead + live
    head_volume = width*p["head_width_m"]*p["head_depth_m"]
    # Interior bent supports two adjacent half bays. Spread the four panel
    # reactions into a line load for the global head screen only.
    total_head = n*length*(breadth*depth*rho) + width*bay*(p["surface_services_kn_m2"]+p["crowd_kn_m2"]) + head_volume*rho
    head_q = total_head/width
    support = quotation["bent_column_lateral_m"]
    overhang = width/2-support
    schedules = {}
    for layer, distribution, run in (("bottom_longitudinal", breadth, length),
                                     ("top_longitudinal", breadth, length),
                                     ("transverse", length, breadth)):
        dia = steel[layer+"_diameter_m"]
        pitch = steel[layer+"_spacing_m"]
        usable = distribution-2*steel["cover_m"]-dia
        count = math.ceil(usable/pitch)+1
        if layer == "transverse":
            count *= 2  # one set in each face
        bar_length = run-2*steel["cover_m"]
        schedules[layer] = dict(count=count, straight_bar_length_m=bar_length,
                                mass_kg=count*bar_length*mat["steel_mass_kg_m3"]*math.pi*dia**2/4)
    bays = round(station["platform_clear_length_m"]/bay)
    if not math.isclose(bays*bay, station["platform_clear_length_m"]):
        raise ValueError("Platform length needs a nonstandard end bay")
    return dict(panel_length_m=length, panel_width_m=breadth, panel_support_span_m=span,
                panel_count_template=bays*n, panel_volume_m3=volume, panel_weight_kn=volume*rho,
                straight_bar_schedule_per_panel=schedules, counted_straight_stock_kg=sum(v["mass_kg"] for v in schedules.values()),
                panel_dead_line_kn_m=dead, panel_live_line_kn_m=live,
                panel_positive_moment_upper_knm=q*span**2/8,
                panel_end_reaction_kn=(breadth*length*depth*rho+bay*width/n*(p["surface_services_kn_m2"]+p["crowd_kn_m2"]))/2,
                head_volume_m3=head_volume, head_tributary_load_kn=total_head,
                symmetric_column_reaction_kn=total_head/2,
                head_midspan_moment_knm=head_q*(support**2-overhang**2)/2,
                head_column_hogging_moment_knm=-head_q*overhang**2/2,
                centre_drain_drop_m=width/2*p["fall_to_centre_fraction"])


def evaluate():
    paths = [DIR/"concept.toml", PARENT/"schedule.json", PARENT/"quotation.toml", CITY/"system.toml"]
    cfg, parent = tomllib.loads(paths[0].read_text()), json.loads(paths[1].read_bytes())
    quote, city = [tomllib.loads(path.read_text()) for path in paths[2:]]
    parent_sources = [CITY/"system.toml", CITY/"system-results.json", PARENT/"quotation.toml",
                      PARENT/"drawing.py", PARENT/"develop.py"]
    if set(parent["sources_sha256"]) != {path.name for path in parent_sources}:
        raise ValueError("Incomplete parent mechanical source register")
    for path in parent_sources:
        if hash_file(path) != parent["sources_sha256"][path.name]:
            raise ValueError("Stale mechanical parent: "+path.name)
    if (parent["network"], quote["supply"], quote["civil"]) != ("first","protected_conductor","10m-separate"):
        raise ValueError("Incompatible Baghdad parent")
    geom = {key: cfg["box"][key] for key in (
        "width_m", "depth_m", "web_m", "slab_m", "solid_end_m", "pad_width_m",
        "pad_length_m", "lift_pick_inset_m", "effective_tendon_eccentricity_m")}
    deck = {k:v for k,v in cfg["platform"].items() if k.endswith("_m") or k in ("panels_across","fall_to_centre_fraction")}
    study = identity([parent["study_physical_id"], geom, deck, cfg["reinforcement"], {k:v for k,v in cfg["pier"].items() if k.endswith("_m")}])
    sources = {str(p.relative_to(CITY)):hash_file(p) for p in paths+[Path(__file__).resolve()]}
    return dict(physical_id=study, evaluation_id=identity([study, sources]), parent_physical_id=parent["study_physical_id"],
                parent_evaluation_id=parent["study_evaluation_id"], source_sha256=sources,
                purpose="Straight bay quotation study", accepted=False,
                track=box_screen(cfg["box"], cfg["materials"], parent["viaduct"], cfg["pier"]),
                platform=platform_screen(cfg["platform"], cfg["reinforcement"], cfg["materials"],
                                         city["station_geometry"], quote["platform"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = json.dumps(evaluate(), indent=2)+"\n"
    path = DIR/"section-results.json"
    if args.check:
        if value != path.read_text():
            raise SystemExit("Stale civil section results")
    else:
        path.write_text(value)
