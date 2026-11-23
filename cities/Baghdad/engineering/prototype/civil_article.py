"""Detail the ten-metre Airport beam and five-metre island bay for a first-article enquiry."""

import csv
import io
import math
from pathlib import Path
import tomllib

from cities.Baghdad.engineering.prototype import car

STRAND_DATA = "https://www.bekaert.com/content/dam/corporate/en/product-catalog/pdfs/Bekaert-Prestressing-Strand-for-Concrete-Reinforcement-Productsheet.pdf"


def bars(length, width, height, web, solid_end, cover, density):
    """Two mating U bars form a perimeter link, with their ends lapped in both slabs."""
    rows = []

    def row(mark, description, diameter, count, developed, geometry):
        rows.append(
            dict(
                mark=mark,
                part=description,
                diameter_mm=diameter * 1000,
                pieces=count,
                developed_length_m=round(developed, 6),
                straight_stock_m=count * developed,
                nominal_kg=count * developed * math.pi * diameter**2 / 4 * density,
                geometry=geometry,
            )
        )

    # Rounding each station avoids a coincident end/field boundary occurring twice.
    first = 0.060
    stations = set()
    for start, end, max_pitch in (
        (first, solid_end, 0.10),
        (solid_end, length - solid_end, 0.20),
        (length - solid_end, length - first, 0.10),
    ):
        n = math.ceil((end - start) / max_pitch)
        stations.update(round(start + i * (end - start) / n, 6) for i in range(n + 1))
    stations = sorted(stations)
    d = 0.012
    w = width - 2 * cover - d
    h = height - 2 * cover - d
    bend_r = 0.036
    lap = 0.400
    # Two quarter circles replace four straight tangent lengths in each U.
    developed = w + h + lap + 2 * bend_r * (math.pi / 2 - 2)
    for hand, sign in (("L", -1), ("R", 1)):
        row(
            "U-" + hand,
            "Perimeter U hoop with transverse lap at both ends",
            d,
            len(stations),
            developed,
            {
                "centreline_web_y_m": sign * w / 2,
                "centreline_z_m": [cover + d / 2, height - cover - d / 2],
                "free_end_y_m": -sign * lap / 2,
                "bend_centreline_radius_m": bend_r,
                "bend_inside_diameter_m": 2 * bend_r - d,
                "number_of_90_degree_bends": 2,
                "overlap_each_leg_m_proposed": lap,
                "x_m": [round(x + sign * 0.0075, 6) for x in stations],
            },
        )

    # The two longitudinal faces of each slab and inner transverse bars close the stock takeoff.
    long_d = 0.012
    ys = [round((i / 11 - 0.5) * (width - 0.21), 6) for i in range(12)]
    for tag, z in [("B1", 0.063), ("B2", 0.133), ("T1", height - 0.063), ("T2", height - 0.133)]:
        row(
            tag,
            "Straight longitudinal slab bars",
            long_d,
            len(ys),
            length - 2 * cover,
            {"axis": "x", "from_x_m": cover, "to_x_m": length - cover, "y_m": ys, "z_m": z},
        )
    inner_trans_d = 0.012
    for tag, z in (("BX", 0.145), ("TX", height - 0.145)):
        row(
            tag,
            "Straight cross bars on slab inner face",
            inner_trans_d,
            len(stations),
            width - 2 * cover,
            {
                "axis": "y",
                "from_y_m": -width / 2 + cover,
                "to_y_m": width / 2 - cover,
                "z_m": z,
                "x_m": stations,
            },
        )
    # Centreline positions, distinct from the longitudinal web strands.
    web_ys = [sign * (width / 2 - cover - d - long_d / 2) for sign in (-1, 1)]
    web_zs = [round(height * f, 6) for f in (0.2, 0.4, 0.6, 0.8)]
    row(
        "W",
        "Outer-face web longitudinal bars",
        long_d,
        len(web_ys) * len(web_zs),
        length - 2 * cover,
        {"axis": "x", "from_x_m": cover, "to_x_m": length - cover, "y_m": web_ys, "z_m": web_zs},
    )
    return rows


def strand_screen(beam, b):
    strand_d = 0.0152
    area = 0.00014
    min_breaking_kn = 261.0
    # The study fraction and loss bracket are hypotheses for price and geometry.
    gross_kn = 0.70 * min_breaking_kn
    losses = (0.15, 0.20, 0.30)
    required = beam["effective_axial_force_for_zero_bottom_stress_kn"]
    per_web = math.ceil(required / (2 * gross_kn * (1 - max(losses))))
    n = 2 * per_web
    e = b["effective_tendon_eccentricity_m"]
    centre = b["depth_m"] / 2 - e
    pitch = 0.070
    ys = [sign * (b["width_m"] / 2 - b["web_m"] / 2) for sign in (-1, 1)]
    zs = [round(centre + (i - (per_web - 1) / 2) * pitch, 6) for i in range(per_web)]
    if min(zs) - strand_d / 2 <= 0.050 or min(b["depth_m"] - z for z in zs) - strand_d / 2 <= 0.050:
        raise ValueError("Strand bank has exhausted the proposed concrete envelope")
    section_modulus = 2 * beam["midspan_I_m4"] / b["depth_m"]

    def stress(force, moment):
        axial = force / beam["midspan_area_m2"] / 1000
        bending = (moment - force * e) / section_modulus / 1000
        return {"top_compression_mpa": axial + bending, "bottom_compression_mpa": axial - bending}

    scenarios = []
    for loss in losses:
        effective = n * gross_kn * (1 - loss)
        scenarios.append(
            {
                "assumed_loss": loss,
                "effective_kn": effective,
                "surplus_over_zero_bottom_tension_kn": effective - required,
                "service_fibres": stress(effective, beam["positive_moment_upper_knm"]),
            }
        )
    return {
        "nominal_diameter_m": strand_d,
        "area_m2": area,
        "catalogue_linear_mass_kg_m": 1.10,
        "catalogue_minimum_breaking_kn": min_breaking_kn,
        "source": STRAND_DATA,
        "studied_initial_force_fraction": 0.70,
        "assumed_losses": list(losses),
        "strand_count": n,
        "axis": "straight along x",
        "strand_y_m": ys,
        "strand_z_m_from_soffit": zs,
        "strand_pitch_m": pitch,
        "centroid_eccentricity_below_centroid_m": e,
        "cast_length_per_strand_m": beam["length_m"],
        "long_line_bed_extra_stock_m": None,
        "embedded_strand_stock_m": n * beam["length_m"],
        "embedded_strand_kg": n * beam["length_m"] * 1.10,
        "zero_bottom_tension_force_kn": required,
        "service_sensitivity": scenarios,
        "initial_force_at_full_transfer_hypothesis_kn": n * gross_kn,
        "full_transfer_zero_applied_moment_diagnostic": stress(n * gross_kn, 0),
        "pick_hogging_at_full_transfer_diagnostic": stress(n * gross_kn, beam["stock_lift_hogging_knm"]),
        "limits": "Gross symmetric middle section. Force fractions and losses are study inputs. End transfer, local bursting, elastic shortening, time history, capacity at release and concrete strengths require independent design.",
    }


def build(record):
    if record["evaluation_id"] != car.identity(
        {k: v for k, v in record.items() if k != "evaluation_id"}
    ) or (
        record["opening"]["candidate_id"] != record["candidate_id"]
        or record["opening"]["bundle"]["span_m"] != 10
    ):
        raise ValueError("Civil detailing requires the matching ten-metre Airport mechanical evaluation")
    concept = car.CITY / "engineering/mechanical/civil/concept.toml"
    config = tomllib.loads(concept.read_text())
    city = tomllib.loads((car.CITY / "system.toml").read_text())
    b = config["box"]
    beam = record["civil"]["track"]
    panel = record["civil"]["station_bay"]
    cover = config["reinforcement"]["cover_m"]
    steel = bars(
        beam["length_m"],
        b["width_m"],
        b["depth_m"],
        b["web_m"],
        b["solid_end_m"],
        cover,
        config["materials"]["steel_mass_kg_m3"],
    )
    prestress = strand_screen(beam, b)
    # Minimum distance from strands to longitudinal web bars, outside U web leg, inner ties and straight slab bars.
    pts = [(y, z) for y in prestress["strand_y_m"] for z in prestress["strand_z_m_from_soffit"]]
    gaps = []
    for y, z in pts:
        radius = prestress["nominal_diameter_m"] / 2
        for bar in steel:
            g = bar["geometry"]
            bar_r = bar["diameter_mm"] / 2000
            if g.get("axis") == "x":
                zs = g["z_m"] if isinstance(g["z_m"], list) else [g["z_m"]]
                gaps.extend(math.hypot(y - by, z - bz) - radius - bar_r for by in g["y_m"] for bz in zs)
            elif g.get("axis") == "y":
                gaps.append(abs(z - g["z_m"]) - radius - bar_r)
            else:
                gaps.append(abs(y - g["centreline_web_y_m"]) - radius - bar_r)
                gaps.extend(abs(z - bz) - radius - bar_r for bz in g["centreline_z_m"])
    clearance = min(gaps)
    if clearance < 0:
        raise ValueError("Strand clashes with proposed bar stock")
    cage_id = car.identity(
        {
            "parent_civil_article": record["civil"]["parent_physical_id"],
            "bar_geometry": steel,
            "strand_pattern": [
                prestress[k]
                for k in (
                    "nominal_diameter_m",
                    "strand_y_m",
                    "strand_z_m_from_soffit",
                    "cast_length_per_strand_m",
                )
            ],
        }
    )
    bearing_w, bearing_l = b["pad_width_m"], b["pad_length_m"]
    lift = beam["reinforced_stock_weight_kn"]
    bay = panel["panel_length_m"] + config["platform"]["panel_joint_m"]
    island = city["station_geometry"]["island_width_m"]
    doors = record["interfaces"]["station_keep_clear_x_m"]
    per_station = panel["panel_count_template"]
    coordinates = city["station_geometry"]
    output = {
        "candidate_id": record["candidate_id"],
        "mechanical_evaluation_id": record["evaluation_id"],
        "physical_id": cage_id,
        "parent_civil_article": record["civil"]["parent_physical_id"],
        "purpose": "First-article reinforcing and straight pretension layout for supplier review",
        "frame": "Beam x from left stock end; y across track from centreline; z up from soffit.",
        "source_sha256": {
            p.relative_to(car.ROOT).as_posix(): car.sha(p.read_bytes())
            for p in (
                Path(__file__),
                concept,
                car.CITY / "system.toml",
                Path(__file__).with_name("civil-guide.md"),
            )
        },
        "bar_schedule_one_beam": steel,
        "straight_and_developed_bar_kg": sum(r["nominal_kg"] for r in steel),
        "strand": prestress,
        "minimum_nominal_strand_to_bar_surface_gap_m": clearance,
        "bar_and_strand_kg_per_beam": prestress["embedded_strand_kg"]
        + sum(r["nominal_kg"] for r in steel),
        "station_panels": {
            "one_panel_straight_bar_schedule": panel["straight_bar_schedule_per_panel"],
            "panels_per_island_template": per_station,
            "concrete_m3_per_panel": panel["panel_volume_m3"],
            "straight_bar_kg_per_island_template": per_station * panel["counted_straight_stock_kg"],
        },
        "quantities": {
            "repeat_beams": record["opening"]["civil"]["beam_count"],
            "series_embedded_strand_length_m_if_repeated": record["opening"]["civil"]["beam_count"]
            * prestress["embedded_strand_stock_m"],
            "floor_and_site_price_change_usd": None,
            "pricing_scope": "Parent capital prices the box, erection and bearing scope with planning rates. Quote replacement work packages including cage and strand. The nominal 25 kN/m³ stock weight already includes reinforcement.",
        },
        "bearing_and_erection": {
            "bearing_units": beam["pad_count"],
            "maximum_screen_pad_kn": beam["highest_pad_reaction_kn"],
            "pad_pressure_mpa": beam["highest_pad_reaction_kn"] / (bearing_w * bearing_l) / 1000,
            "stock_end_side_margins_m": [beam["pad_end_margin_m"], beam["pad_side_margin_m"]],
            "thermal_travel_over_span_mm_at_45K": beam["bearing_span_m"] * 1e-5 * 45 * 1000,
            "thermal_basis": "One guided expansion end; assumed 10 micrometres/m/K. Add long-term shortening, temperature range and movement limits from the project.",
            "dead_installed_end_reaction_kn": beam["dead_end_reaction_kn"],
            "two_equal_jacks_per_end_dead_kn_each": beam["dead_end_reaction_kn"] / 2,
            "stock_weight_kn": lift,
            "two_lift_lines_from_stock_ends_m": [
                b["lift_pick_inset_m"],
                beam["length_m"] - b["lift_pick_inset_m"],
            ],
            "static_lift_moment_limits_knm": [
                beam["stock_lift_hogging_knm"],
                beam["stock_lift_midspan_knm"],
            ],
            "sling_leg_kn_at_60deg_for_four_equal_legs": beam["sling_leg_kn_equal_four_point"],
            "two_loaded_legs_with_10pct_dynamic_allowance_kn_each": 1.10
            * lift
            / (2 * math.sin(math.radians(b["sling_angle_above_horizontal_deg"]))),
            "approved_jack_and_crane_ratings": None,
        },
        "station_interfaces": {
            "door_openings_per_boarding_side": len(doors),
            "edge_reserved_length_per_opening_m": doors[0][1] - doors[0][0],
            "static_level_horizontal_gap_m": coordinates["straight_platform_edge_offset_m"]
            - city["vehicle_geometry"]["body_width_m"] / 2,
            "vehicle_floor_above_rail_m": city["vehicle_geometry"]["floor_above_rail_m"],
            "measured_height_difference_m": None,
            "platform_side_width_m": island / 2,
            "surface_fall": config["platform"]["fall_to_centre_fraction"],
            "edge_to_centre_drop_m": panel["centre_drain_drop_m"],
            "catchment_per_bay_m2": bay * island,
            "rainfall_runoff_l_s": [
                {
                    "rain_mm_h": r,
                    "runoff_coefficient_assumed": 0.95,
                    "l_s_per_bay": r * bay * island * 0.95 / 3600,
                }
                for r in (50, 100)
            ],
            "circulation_sensitivities": [
                {
                    "alighting_people": sets * city["vehicle"]["normal_places_per_train"],
                    "effective_exit_width_m_assumed": 3,
                    "flow_people_m_s_assumed": 0.8,
                    "minutes_at_constant_flow": sets
                    * city["vehicle"]["normal_places_per_train"]
                    / (3 * 0.8 * 60),
                }
                for sets in (1, 2)
            ],
            "surveyed_step_free_route": None,
        },
        "open": [
            "Beam ULS shear/torsion, punching, fatigue, crack control, strand transfer/end bursting, reinforcement congestion and temporary stages",
            "Soil, seismic/flood actions, offsets and foundation settlements; bearing/jack restraint, anchors, crane at operating radius and method",
            "Actual train/platform gaps and steps at curves and in service; outlets and rainfall, lifts, egress paths and real passenger-flow observations",
        ],
        "fabrication_released": False,
        "physical_accepted": False,
    }
    output["evaluation_id"] = car.identity(output)
    return output


def section_drawing(result):
    """Project the actual trial bar/strand centres onto a transverse section."""
    from xml.etree.ElementTree import Element, SubElement, tostring

    root = Element(
        "svg",
        {
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": "0 0 1000 610",
            "role": "img",
            "aria-labelledby": "title",
        },
    )
    SubElement(root, "title", id="title").text = "Airport beam cage and straight strand positions"
    SubElement(root, "rect", width="100%", height="100%", fill="white")

    def text(x, y, content, size=17):
        SubElement(
            root,
            "text",
            {
                "x": str(x),
                "y": str(y),
                "font-size": str(size),
                "font-family": "sans-serif",
                "fill": "#1b3548",
            },
        ).text = content

    def xy(y, z):
        return (320 + 245 * y, 486 - 245 * z)

    def pt(y, z):
        x, v = xy(y, z)
        return f"{x:.3f},{v:.3f}"

    cfg = tomllib.loads((car.CITY / "engineering/mechanical/civil/concept.toml").read_text())["box"]
    w, h, slab, web = cfg["width_m"], cfg["depth_m"], cfg["slab_m"], cfg["web_m"]

    def rectangle(y, z, width, height, fill):
        x, v = xy(y, z + height)
        SubElement(
            root,
            "rect",
            {
                "x": str(x),
                "y": str(v),
                "width": str(width * 245),
                "height": str(height * 245),
                "fill": fill,
                "stroke": "#6f8187",
            },
        )

    text(35, 46, "Ten-metre guidebeam   /   Proposed precast cage", 27)
    text(
        35,
        78,
        "Section in the hollow region, looking in the +x direction. Both transverse hoop planes are projected.",
        15,
    )
    rectangle(-w / 2, 0, w, h, "#e0e5e4")
    rectangle(-w / 2 + web, slab, w - 2 * web, h - 2 * slab, "white")

    def circle(y, z, r, fill):
        x, v = xy(y, z)
        SubElement(root, "circle", {"cx": str(x), "cy": str(v), "r": str(r * 245), "fill": fill})

    for row in result["bar_schedule_one_beam"]:
        g = row["geometry"]
        if g.get("axis") == "x":
            for y in g["y_m"]:
                for z in (g["z_m"] if isinstance(g["z_m"], list) else [g["z_m"]]):
                    circle(y, z, row["diameter_mm"] / 2000, "#152d43")
        elif g.get("axis") == "y":
            SubElement(
                root,
                "polyline",
                {
                    "points": " ".join(pt(y, g["z_m"]) for y in (g["from_y_m"], g["to_y_m"])),
                    "stroke": "#759695",
                    "stroke-width": "2",
                    "fill": "none",
                },
            )
        else:
            y, y0 = g["centreline_web_y_m"], g["free_end_y_m"]
            low, high = g["centreline_z_m"]
            SubElement(
                root,
                "polyline",
                {
                    "points": " ".join(
                        pt(py, pz) for py, pz in ((y0, low), (y, low), (y, high), (y0, high))
                    ),
                    "stroke": "#087a6d",
                    "stroke-width": "2.7",
                    "stroke-linejoin": "round",
                    "fill": "none",
                },
            )
    strand = result["strand"]
    for y in strand["strand_y_m"]:
        for z in strand["strand_z_m_from_soffit"]:
            circle(y, z, strand["nominal_diameter_m"] / 2, "#cd5716")
    for i, t in enumerate(
        [
            f"{w:.3f} m overall width",
            f"{h:.3f} m overall depth",
            f"{web*1000:.0f} mm webs  /  {slab*1000:.0f} mm slabs",
            f'{strand["strand_count"]} straight strands, shown in orange',
            "Longitudinal bars shown in dark blue",
            "U laps at top and bottom, shown in green",
            "Inspect lap and end-block congestion in the mould",
        ]
    ):
        text(593, 174 + i * 43, t, 16)
    text(
        35,
        533,
        "Beam stock datum at soffit. Use the station and bar coordinates in civil-article.json for shop development.",
        15,
    )
    text(35, 572, "Cage " + result["physical_id"], 13)
    return tostring(root, encoding="utf-8")


def artifacts(record):
    result = build(record)
    buff = io.StringIO()
    writer = csv.writer(buff, lineterminator="\n")
    writer.writerow(
        [
            "mark",
            "part",
            "diameter_mm",
            "pieces_per_beam",
            "developed_length_each_m",
            "nominal_stock_kg_per_beam",
        ]
    )
    for r in result["bar_schedule_one_beam"]:
        writer.writerow(
            [r[k] for k in ("mark", "part", "diameter_mm", "pieces", "developed_length_m", "nominal_kg")]
        )
    p = result["strand"]
    writer.writerow(
        [
            "PS",
            "Straight strand, embedded stock only",
            p["nominal_diameter_m"] * 1000,
            p["strand_count"],
            p["cast_length_per_strand_m"],
            p["embedded_strand_kg"],
        ]
    )
    return result, {
        "civil-article.json": car.encode(result),
        "beam-cage-section.svg": section_drawing(result),
        "beam-bar-strand-schedule.csv": buff.getvalue().encode(),
        "civil-guide.md": Path(__file__).with_name("civil-guide.md").read_bytes(),
    }
