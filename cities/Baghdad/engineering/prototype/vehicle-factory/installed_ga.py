"""Draft the Airport car arrangement from the issued first-article packet."""

import argparse
import csv
from hashlib import sha256
from html import escape
import io
import json
from pathlib import Path
from zipfile import ZipFile


HERE = Path(__file__).resolve().parent
PACKET = HERE.parent / "airport-prototype.zip"
MEMBERS = (
    "mechanical.json", "fitout-interfaces.json", "opening.json", "opening-bom.csv",
    "returns/weights.json",
)


def read_sources():
    with ZipFile(PACKET) as packet:
        manifest = json.loads(packet.read("manifest.json"))
        records = {name: packet.read(name) for name in MEMBERS}
    digests = {name: sha256(data).hexdigest() for name, data in records.items()}
    if any(manifest["sha256"][name] != digest for name, digest in digests.items()):
        raise ValueError("Packet member hash mismatch")
    mech, fit, opening, weights = (
        json.loads(records[name]) for name in (*MEMBERS[:3], MEMBERS[-1])
    )
    candidate = manifest["candidate_id"]
    if {mech["candidate_id"], fit["candidate_id"], opening["candidate_id"]} != {candidate}:
        raise ValueError("Mixed vehicle candidate")
    if not fit["frame_revision"] == mech["frame_revision"] == opening["bundle"]["vehicle_revision"]:
        raise ValueError("Mixed vehicle frame revisions")
    if fit["article_evaluation_id"] != mech["evaluation_id"]:
        raise ValueError("Mixed mechanical article evaluations")
    bom = list(csv.DictReader(io.StringIO(records["opening-bom.csv"].decode())))
    return mech, fit, opening, weights, bom, digests


LOCATION = {
    "Braced steel body": ("stock positioned", "Body stock pieces; finished skin and trim open"),
    "Removable powered bogie": ("stock positioned", "Bogie A/B bare frame boxes and centres"),
    "Wheelset": ("interface positioned", "Four axle x positions; wheel and journal geometry open"),
    "Axlebox bearing positions": ("interface positioned", "At eight primary pad locations; bearing centres and sizes open"),
    "Axle drive module": ("interface positioned", "Four driven axle planes; mount and inverter locations open"),
    "Primary spring interface": ("interface positioned", "Eight primary pad faces; spring and axlebox geometry open"),
    "Secondary spring interface": ("interface positioned", "Four opposed pad pairs; spring, stop and travel open"),
    "Door opening and controller": ("partial", "Eight steel portals; moving leaves reserved; controller location open"),
    "Roof HVAC module": ("study zone", "Two roof stations along the centreline; actual mounting, footprint and height open"),
    "Chord splice": ("stock positioned", "Splice planes referenced to sill and cantrail cuts; joining detail open"),
    "Post-end joint": ("interface positioned", "Jamb and end post ends; joining detail open"),
    "Crossmember-end joint": ("interface positioned", "Floor, roof and bolster tie ends; joining detail open"),
    "Brace-end connection": ("interface positioned", "Brace and gusset stock locations; joining detail open"),
    "Transom and saddle ends": ("interface positioned", "Bogie stock end locations; joining detail open"),
    "Primary and secondary pad attachments": ("interface positioned", "Bogie pad faces; attachment detail open"),
    "sliding leaves": ("reserved sweep", "Sixteen nominal swept leaf boxes; fitted door equipment open"),
    "flush liner screws": ("interface positioned", "Liner fastening coordinates in mechanical.json; countersink and grip open"),
    "liner threaded receivers": ("interface positioned", "Paired to screw locations; blind-side installation detail open"),
    "Floor, skin, glazing, seats, wheelchair fittings and insulation": (
        "study zone", "Saloon zones on the +1.00 m nominal floor; seat and wheelchair positions open"
    ),
    "tcms_nodes": ("study zone", "One planned node per car; central services study zone only"),
}

SUPPLEMENT = (
    ("Onboard conductor contact sets", "", "", "onboard_contact_sets", "Quantity at fleet level; car roles and collector position open"),
    ("Train couplers, gangways and inter-car services", "", "", "", "Vehicle-end interface only; coupling and articulation envelopes open"),
    ("Rescue/tow attachment and onboard recovery fittings", "", "", "", "Coupler and recovery load schedule, access and storage open"),
    ("LV/emergency supply, batteries and auxiliaries", "", "", "", "Service sizing, endurance, protection, disconnect and location open"),
    ("Passenger communications, lighting and emergency equipment", "", "", "", "Installed quantities, power, coverage and location open"),
    ("Lifting/jacking and skid/retention equipment", "", "", "", "Approved loads, tool envelopes, locations and permanent provisions open"),
    ("Identification, finishes, coatings, fluids and joining consumables", "", "", "", "Net installed mass and quantities open"),
)


def fitout_bom(opening, bom):
    """Preserve source counts and keep detailed components inside owning groups."""
    rows = []
    for row in bom:
        scope, name = row["scope"], row["item"]
        if scope not in {"cut material", "installed allocation", "door detail"}:
            continue
        fallback = ("stock positioned", "Gross modelled cut stock; see mechanical piece register") if scope == "cut material" else (
            "unlocated", "Installed positions and full volumes await supplier definition"
        )
        status, note = LOCATION.get(name, fallback)
        rows.append([scope, name, row["unit"], row["per_car"], row["per_train"], row["opening_quantity"],
                     status, note, row["basis"], "", ""])
    for name, car, train, key, note in SUPPLEMENT:
        quantity = opening["power"]["maintenance_quantities"].get(key, "")
        rows.append(["supplementary installed allocation", name, "each", car, train, quantity,
                     "unlocated", note, "Await installed breakdown and supplier drawing", "", ""])
    buf = io.StringIO(newline="")
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["source_scope", "group", "unit", "per_car", "per_train", "opening_quantity",
                     "geometry_status", "location_or_gap", "quantity_basis", "installed_mass_kg", "drawing_or_evidence"])
    writer.writerows(rows)
    return buf.getvalue()


def arrangement(mech, fit):
    door = mech["doorway"]
    spec = door["specification"]
    centres = [round((lo + hi) / 2, 6) for lo, hi in zip(
        door["rough_jamb_axes_x_m"][::2], door["rough_jamb_axes_x_m"][1::2], strict=True
    )]
    half_wall = fit["car_width_m"] / 2
    apertures = [{
        "centre_x_m": x, "wall_reference_y_m": sign * half_wall,
        "rough_width_m": width,
        "leaf_sweep_x_m": [round(x - spec["leaf_closed_width_m"] - spec["leaf_travel_m"], 6),
                           round(x + spec["leaf_closed_width_m"] + spec["leaf_travel_m"], 6)],
        "leaf_plane_y_m": sign * spec["leaf_plane_y_m"],
        "leaf_thickness_m": spec["leaf_thickness_m"],
        "leaf_sweep_z_m": [spec["leaf_bottom_m"], round(spec["leaf_bottom_m"] + spec["leaf_height_m"], 6)],
    } for sign in (-1, 1) for x, width in zip(
        centres, door["rough_widths_m"][:len(centres)], strict=True
    )]
    # These are longitudinal search intervals derived from adjacent door sweeps.
    # They imply no available section, mount strength or maintainable access.
    one_side = apertures[:len(centres)]
    zones = [list(bounds) for bounds in zip(
        [a["leaf_sweep_x_m"][1] for a in one_side[:-1]],
        [a["leaf_sweep_x_m"][0] for a in one_side[1:]], strict=True
    )]
    bogies = []
    for bogie in fit["bogies"]:
        pivot = bogie["body_from_bogie_translation_m"][0]
        pads = [{**pad, "body_face_centre_m": [
            round(pivot + pad["local_face_centre_mm"][0] / 1000, 6),
            pad["local_face_centre_mm"][1] / 1000,
            pad["local_face_centre_mm"][2] / 1000,
        ]} for pad in bogie["pads"]]
        bogies.append({**bogie, "pads": pads})
    axle_x = [round(b["body_from_bogie_translation_m"][0] + axle / 1000, 6)
              for b in bogies for axle in b["local_axle_planes_x_mm"]]
    if axle_x != mech["interfaces"]["body_from_axle_x_m"] or any(lo >= hi for lo, hi in zones):
        raise ValueError("Invalid axle or interior study geometry")
    if len(apertures) != len(door["rough_widths_m"]) or any(
        a["rough_width_m"] != width for a, width in zip(apertures, door["rough_widths_m"], strict=True)
    ):
        raise ValueError("Door arrangement differs from the article")
    return {
        "datum": mech["frame_axis"], "car_length_m": fit["car_length_m"],
        "car_width_m": fit["car_width_m"], "nominal_floor_railhead_z_m": fit["floor_z_m"],
        "body_stock_top_railhead_z_m": max(
            p["upper_m"][2] for p in mech["pieces"] if p["assembly"] == "body"
        ),
        "stock_pieces": mech["pieces"], "bogies": bogies, "axle_planes_x_m": axle_x,
        "door_apertures": apertures, "saloon_study_intervals_x_m": zones,
        "roof_study_points_xy_m": [[round((lo + hi) / 2, 6), 0] for lo, hi in (zones[0], zones[-1])],
        "underfloor_services_study_x_m": 0,
        "formation_body_from_car_x_m": mech["interfaces"]["formation_body_from_car_x_m"],
    }


def drawing(ga, binding):
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 706" role="img" aria-labelledby="title desc">',
        '<title id="title">Baghdad Airport installed-car general arrangement</title>',
        '<desc id="desc">Scaled plan and elevation of the straight vehicle datum. Steel stock, door reservations, axle and pad interfaces, and separate study zones are shown.</desc>',
        '<style>text{font:15px sans-serif;fill:#1e3547}.title{font:bold 28px sans-serif}.heading{font:bold 18px sans-serif}'
        '.small{font:12px sans-serif}.mono{font:12px monospace}rect,path,circle{stroke-width:1.1}.outline{fill:none;stroke:#263e51}'
        '.steel{fill:#a8b8c7;stroke:#405f7b}.bogie{fill:#698096;stroke:#354d63}'
        '.door{fill:#eeac69;fill-opacity:.65;stroke:#9a4b13}.study{fill:#c8eae6;fill-opacity:.65;stroke:#126965;stroke-dasharray:4 3}'
        '.datum{stroke:#647c92;stroke-dasharray:6 4}.iface{fill:#fff;stroke:#674495;stroke-width:2}.dimension{stroke:#374c5d}</style>',
        '<rect width="1200" height="706" fill="white"/>',
    ]
    scale = 57

    def px(x):
        return 600 + x * scale

    def text(x, y, value, style=""):
        parts.append(f'<text x="{x:g}" y="{y:g}" class="{style}">{escape(value)}</text>')

    def line(x0, y0, x1, y1, style):
        parts.append(f'<path d="M{x0:g} {y0:g}L{x1:g} {y1:g}" class="{style}"/>')

    def box(lo, hi, project, style):
        x, y = project(lo)
        xx, yy = project(hi)
        parts.append(f'<rect x="{x:g}" y="{min(y, yy):g}" width="{xx-x:g}" height="{abs(yy-y):g}" class="{style}"/>')

    def marker(x, y, style):
        parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="5" class="{style}"/>')

    def plan(p):
        return px(p[0]), 241 - p[1] * scale

    def elevation(p):
        return px(p[0]), 562 - p[2] * scale

    def dim(lo, hi, y, label):
        line(px(lo), y, px(hi), y, "dimension")
        for x in (lo, hi):
            line(px(x), y - 5, px(x), y + 5, "dimension")
        text((px(lo) + px(hi)) / 2 - 37, y - 8, label, "small")

    length, width = ga["car_length_m"], ga["car_width_m"]
    half_length, half_width = length / 2, width / 2
    floor = ga["nominal_floor_railhead_z_m"]
    text(50, 43, "Baghdad Airport  /  Representative car general arrangement", "title")
    text(50, 71, "Straight installed pose  •  x forward   y left   z up  •  railhead z = 0  •  metres")
    text(50, 104, "Plan   x–y", "heading")
    dim(-half_length, half_length, 142, f"{length:g} m nominal")
    box((-half_length, -half_width, 0), (half_length, half_width, 0), plan, "outline")
    line(px(-half_length), 241, px(half_length), 241, "datum")
    text(1096, 239, f"{width:g} m", "small")
    text(1096, 254, "nominal", "small")
    text(55, 168, "+y", "small")
    for bogie in ga["bogies"]:
        lo, hi = bogie["installed_box_vehicle_m"]
        box(lo, hi, plan, "bogie")
        for pad in bogie["pads"]:
            marker(*plan(pad["body_face_centre_m"]), "iface")
    for lo, hi in ga["saloon_study_intervals_x_m"]:
        box((lo, -half_width, 0), (hi, half_width, 0), plan, "study")
    for x, y in ga["roof_study_points_xy_m"]:
        marker(*plan((x, y, 0)), "study")
    marker(*plan((ga["underfloor_services_study_x_m"], 0, 0)), "study")
    for door in ga["door_apertures"]:
        lo, hi = door["leaf_sweep_x_m"]
        y = door["leaf_plane_y_m"]
        thickness = door["leaf_thickness_m"]
        box((lo, y - thickness / 2, 0), (hi, y + thickness / 2, 0), plan, "door")
    for x in ga["axle_planes_x_m"]:
        line(px(x), 318, px(x), 332, "datum")
        text(px(x) - 12, 348, f"{x:g}", "small")
    text(50, 369, "Elevation   x–z   •   near side", "heading")
    for piece in ga["stock_pieces"]:
        lo, hi = piece["lower_m"], piece["upper_m"]
        if piece["assembly"] == "body" and hi[1] <= 0 and piece["part"] not in {"brace", "gusset"}:
            box(lo, hi, elevation, "steel")
    for bogie in ga["bogies"]:
        box(*bogie["installed_box_vehicle_m"], elevation, "bogie")
        marker(*elevation(bogie["body_from_bogie_translation_m"]), "iface")
    for door in ga["door_apertures"]:
        if door["wall_reference_y_m"] < 0:
            lo, hi = door["leaf_sweep_x_m"]
            z0, z1 = door["leaf_sweep_z_m"]
            box((lo, 0, z0), (hi, 0, z1), elevation, "door")
    for x in ga["axle_planes_x_m"]:
        line(px(x), 513, px(x), 562, "datum")
    for z, label in ((0, "Railhead"), (floor, f"Floor +{floor:.2f} m")):
        _, y = elevation((0, 0, z))
        line(px(-half_length), y, px(half_length), y, "datum")
        text(1096, y + 4, label, "small")
    text(340, 582, "Bogie A", "small")
    text(837, 582, "Bogie B", "small")
    text(50, 616, "Main steel stock and bare bogie boxes")
    text(392, 616, "Door-leaf sweep reservation")
    text(746, 616, "Bogie / pad interfaces")
    text(50, 642, "Dashed green  •  Saloon study intervals, roof pack study points and centre service study point", "small")
    text(50, 671, "Frame " + binding["frame_revision"] + "  •  Issue for fitout study and quotation", "mono")
    return "\n".join(parts + ["</svg>", ""])


def outputs():
    mech, fit, opening, weights, bom, digests = read_sources()
    basis = {
        "candidate_id": mech["candidate_id"],
        "frame_revision": mech["frame_revision"],
        "opening_evaluation_id": opening["evaluation_id"],
    }
    if weights["basis"] != basis or weights["mass_groups"]["basis"] != basis:
        raise ValueError("Mixed weights and geometry identities")
    ga = arrangement(mech, fit)
    csv_text = fitout_bom(opening, bom)
    binding = {
        **basis, "mechanical_evaluation_id": mech["evaluation_id"],
        "fitout_evaluation_id": fit["evaluation_id"], "packet_member_sha256": digests,
        "generator_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    svg = drawing(ga, binding)
    summary = {
        **binding, "geometry": ga, "purpose": "Nominee installed-car arrangement for fitout study and quotation",
        "fabrication_released": False, "physical_accepted": False,
        "complete_installed_tare_kg": None,
        "gross_stock_kg_per_car": mech["mass"]["cut_kg_per_car"],
        "mass_return_groups": list(weights["mass_groups"]["train_mass_groups"]),
        "axle_return_ids": list(weights["axle_weighing"]["readings"]),
        "outputs_sha256": {name: sha256(data.encode()).hexdigest() for name, data in (
            ("installed-ga.svg", svg), ("installed-fitout-bom.csv", csv_text)
        )},
    }
    summary["evaluation_id"] = sha256(json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"installed-ga.json": json.dumps(summary, indent=2, sort_keys=True) + "\n",
            "installed-ga.svg": svg, "installed-fitout-bom.csv": csv_text}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare generated bytes with the checked-in draft")
    parser.add_argument("--output-dir", type=Path, default=HERE)
    args = parser.parse_args()
    for name, content in outputs().items():
        path = args.output_dir / name
        if args.check:
            if path.read_bytes() != content.encode():
                parser.exit(1, f"Stale vehicle draft: {path}\n")
        else:
            path.write_bytes(content.encode())


if __name__ == "__main__":
    main()
