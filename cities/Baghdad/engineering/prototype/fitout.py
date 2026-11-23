"""Issue a dimensioned powered-bogie jig sheet and equipment interface enquiry."""

import csv
from html import escape
import io
import json
from pathlib import Path
import tomllib

from cities.Baghdad.engineering.prototype import car

# Supplier records apply to the complete car unless the quantity column names a position.
ENQUIRIES = (
    (
        "Wheelset and bearings",
        "4 wheelsets / 8 bearing positions",
        "Axle plane and corresponding primary seats",
        "Wheel diameter, gauge, back-to-back, journal fit, shoulder and bearing endplay",
        "Identify serials and wheel profile. Record matched fits and endplay after assembly; demonstrate press and bearing extraction access.",
    ),
    (
        "Primary suspension",
        "8 seat positions",
        "Primary pad undersides",
        "Seated height, shim and fastener pattern, axlebox guidance, rebound and jounce stops",
        "Record plate flatness and corner heights; articulate unloaded and loaded axlebox to each stop and measure clearance.",
    ),
    (
        "Secondary suspension",
        "4 seat pairs",
        "Paired lower and upper spring faces",
        "Static stack, tolerance, fastener and retention details, bump and rebound travel, yaw envelope",
        "Survey all four gaps, tare and loaded. Record residual travel and hose, pocket and bolster clearance through roll and yaw.",
    ),
    (
        "Motor and gearbox",
        "4 driven axle positions",
        "Axle planes and adjacent transom stock",
        "Motor, gearbox and torque-link datum, mount reaction loads, shaft alignment, fastener grip and cooling connectors",
        "Check backlash and alignment to supplier limits. Sweep assembly, sling and tool through the defined removal path.",
    ),
    (
        "Brake and parking hold",
        "2 brake controllers; disc and caliper counts open",
        "Wheelset planes",
        "Disc, caliper, actuator, wear stroke, manual release, hose and connector datums",
        "Check full travel at new and worn-pad limits, release access and feedback with the selected equipment.",
    ),
    (
        "HVAC and body fitout",
        "Supplier to declare quantity",
        "Body railhead datum, roof ties, door pockets and floor",
        "Pack bounding box and centre of gravity, isolators, bolt coordinates, ducts, drains, harness loops, filter extraction and lifting travel",
        "Inspect load introduction into roof ties; prove access, drain fall and full filter replacement through the finished body and service gauge.",
    ),
    (
        "Traction, feedback and cooling",
        "Supplier to declare individual circuits",
        "Body-to-bogie disconnect at each exchange interface",
        "Connector pins, retention clips, hose travel, minimum bend radius, isolation and capped service ends",
        "Sweep yaw, roll and full suspension stroke with connections made; verify isolation, drainage, slack and strain relief during exchange.",
    ),
    (
        "Exchange pallet and body stands",
        "2 exchange interfaces",
        "Bogie frame swept box and service lane",
        "Equipped outer box, wheel chocks, pallet projections, lift points and capacities, stand footprints, hoist and tool sweeps",
        "Witness supported disconnection, full extraction, lateral transfer, replacement and reconnect. Measure the smallest clearance at each pass.",
    ),
)


def build(article):
    if article["evaluation_id"] != car.identity(
        {k: v for k, v in article.items() if k != "evaluation_id"}
    ):
        raise ValueError("Use the intact prototype article")
    opening = article["opening"]
    if (
        opening["candidate_id"] != article["candidate_id"]
        or opening["bundle"]["vehicle_revision"] != article["frame_revision"]
    ):
        raise ValueError("Bogie and opening must share the frame revision")
    source = car.CITY / "system.toml"
    if opening["sources"]["cities/Baghdad/system.toml"] != car.sha(source.read_bytes()):
        raise ValueError("The body geometry source has changed")
    geom = tomllib.loads(source.read_text())["vehicle_geometry"]
    bogies = []
    pieces = article["pieces"]

    for assembly in article["interfaces"]["bogies"]:
        pivot, y0, z0 = assembly["body_from_bogie_translation_m"]
        if assembly["rotation_deg"] != [0, 0, 0] or y0 or z0:
            raise ValueError("This sheet requires level bogies on straight track")
        pads = []
        grouped = [p for p in pieces if p["assembly"] == assembly["assembly"]]
        for p in grouped:
            if p["part"] not in ("primary_underside", "secondary_top"):
                continue
            lo, hi = p["lower_m"], p["upper_m"]
            x, y = [(lo[i] + hi[i]) / 2 for i in range(2)]
            primary = p["part"] == "primary_underside"
            paired = [
                q
                for q in pieces
                if q["part"] == "secondary_body"
                and q["lower_m"][0] <= x <= q["upper_m"][0]
                and q["lower_m"][1] <= y <= q["upper_m"][1]
            ]
            if not primary and len(paired) != 1:
                raise ValueError("Missing mating upper plate")
            pads.append(
                {
                    "piece": p["id"],
                    "type": p["part"],
                    "local_face_centre_mm": [
                        round((x - pivot) * 1000, 3),
                        round(y * 1000, 3),
                        round((lo[2] if primary else hi[2]) * 1000, 3),
                    ],
                    "pad_xyz_mm": [round((b - a) * 1000, 3) for a, b in zip(lo, hi, strict=True)],
                    "upper_piece": None if primary else paired[0]["id"],
                    "upper_face_z_mm": None if primary else round(paired[0]["lower_m"][2] * 1000, 3),
                    "stock_face_gap_mm": (
                        None if primary else round((paired[0]["lower_m"][2] - hi[2]) * 1000, 3)
                    ),
                }
            )
        axles = sorted({p["local_face_centre_mm"][0] for p in pads if p["type"] == "primary_underside"})
        if len(pads) != 6 or len(axles) != 2:
            raise ValueError("Each bogie needs four primary and two secondary pads")
        bogies.append(
            {
                **assembly,
                "pads": pads,
                "local_axle_planes_x_mm": axles,
                "stock_piece_ids": [p["id"] for p in grouped],
            }
        )
    record = {
        "candidate_id": article["candidate_id"],
        "article_evaluation_id": article["evaluation_id"],
        "frame_revision": article["frame_revision"],
        "sources": {
            p.relative_to(car.ROOT).as_posix(): car.sha(p.read_bytes()) for p in (Path(__file__), source)
        },
        "datum": article["interfaces"]["origin_convention"],
        "car_length_m": geom["car_body_length_m"],
        "car_width_m": geom["body_width_m"],
        "floor_z_m": geom["floor_above_rail_m"],
        "bogies": bogies,
        "evidence": "Proposed stock and jig datums from design geometry. As-built dimensions, fitted tolerances and equipped sweeps await supplier and workshop evidence.",
        "fabrication_released": False,
        "physical_accepted": False,
    }
    return {**record, "evaluation_id": car.identity(record)}


def sheet(case, pieces):
    bogie = case["bogies"][0]
    pivot = bogie["body_from_bogie_translation_m"][0]
    bounds = bogie["installed_box_vehicle_m"]
    width, length = [round((bounds[1][i] - bounds[0][i]) * 1000) for i in (1, 0)]
    ax = bogie["local_axle_planes_x_mm"]
    primary = next(p for p in bogie["pads"] if p["type"] == "primary_underside")
    secondary = next(p for p in bogie["pads"] if p["type"] == "secondary_top")
    output = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 650" role="img" aria-labelledby="title desc">',
        '<title id="title">Powered bogie jig and installed datums</title><desc id="desc">Scaled plan of a bare powered bogie with axle planes, seat positions, supporting members and dimensions.</desc>',
        '<rect width="1000" height="650" fill="white"/><g font-family="sans-serif" fill="#172f39">',
    ]

    def label(x, y, t, size=16):
        output.append(f'<text x="{x}" y="{y}" font-size="{size}">{escape(str(t))}</text>')

    label(36, 45, "Powered bogie • jig and spring interfaces", 28)
    label(
        36, 76, "Bare stock plan  /  local millimetres  /  +x to the right, +y up  /  rail head at z = 0"
    )
    ox, oy, scale = 305, 324, 0.17
    colours = {
        "bogie_side": "#d2dfe0",
        "transom": "#bacacb",
        "saddle": "#b1bcbd",
        "primary_underside": "#f3c06f",
        "secondary_top": "#63af98",
    }
    for p in sorted(
        (p for p in pieces if p["assembly"] == bogie["assembly"]),
        key=lambda p: p["part"] in ("primary_underside", "secondary_top"),
    ):
        lo, hi = p["lower_m"], p["upper_m"]
        x, y = ox + (lo[0] - pivot) * 1000 * scale, oy - hi[1] * 1000 * scale
        output.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{(hi[0]-lo[0])*1000*scale:.2f}" height="{(hi[1]-lo[1])*1000*scale:.2f}" fill="{colours[p["part"]]}" stroke="#365458"><title>{p["id"]}</title></rect>'
        )
    for a in ax:
        x = ox + a * scale
        output.append(f'<path d="M{x} 114 V535" stroke="#54666c" stroke-dasharray="5 4"/>')
        label(x - 27, 551, f"{a:+.0f}", 14)
    label(180, 111, f"{length} overall × {width} wide")
    label(142, 578, f"{ax[1]-ax[0]:.0f} between axle planes")
    label(594, 132, "Primary • four underside seats", 19)
    label(594, 161, f"Centres y ±{abs(primary['local_face_centre_mm'][1]):.0f} on axle planes")
    label(
        594,
        185,
        f"Pad {' × '.join(f'{n:g}' for n in primary['pad_xyz_mm'])}   /   lower face z {primary['local_face_centre_mm'][2]:g}",
    )
    label(594, 232, "Secondary • two upper seats", 19)
    label(594, 261, f"Centres x 0, y ±{abs(secondary['local_face_centre_mm'][1]):.0f}")
    label(594, 285, f"Lower face of car mounting plate z {secondary['upper_face_z_mm']:g}")
    label(594, 309, f"Top face of bogie pad z {secondary['local_face_centre_mm'][2]:g}")
    label(594, 333, f"Space for spring and shims {secondary['stock_face_gap_mm']:g}")
    label(594, 386, "Car and workshop datums", 19)
    centres = [b["body_from_bogie_translation_m"][0] for b in case["bogies"]]
    label(594, 415, f"Bogie origins at car x {centres[0]:+.3f}, {centres[1]:+.3f} m")
    label(594, 439, f"Floor +{case['floor_z_m']:.3f} m   /   body width {case['car_width_m']:.3f} m")
    label(594, 463, f"Outward stock travel {abs(bogie['signed_outward_travel_m']):.3f} m")
    label(594, 487, f"Exchange lane width {bogie['service_lane_clear_width_m']:.3f} m")
    label(594, 530, "Supplier wheelset, drive and brake envelopes", 15)
    label(594, 552, "and installation tolerances await return.", 15)
    label(36, 618, "Frame revision " + case["frame_revision"], 13)
    return ("".join(output) + "</g></svg>\n").encode()


def artifacts(article):
    case = build(article)
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(
        (
            "candidate_id",
            "frame_revision",
            "interface",
            "quantity_per_car",
            "reference",
            "supplier_to_define",
            "inspection_or_exchange_trial",
            "supplier_drawing_revision",
            "serial_and_attachment",
            "proposed_limits_and_units",
            "as_built_value_and_units",
            "measured_margin_and_units",
            "reviewer_and_date",
        )
    )
    for row in ENQUIRIES:
        writer.writerow((case["candidate_id"], case["frame_revision"], *row, "", "", "", "", "", ""))
    return {
        "powered-bogie-sheet.svg": sheet(case, article["pieces"]),
        "fitout-interfaces.json": (json.dumps(case, sort_keys=True, indent=2) + "\n").encode(),
        "returns/fitout.csv": stream.getvalue().encode(),
        "fitout-guide.md": Path(__file__).with_name("fitout-guide.md").read_bytes(),
    }
