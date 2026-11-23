"""Draw and index the source-bound body-to-bogie suspension interfaces."""

import argparse
import csv
import io

from installed_ga import HERE, arrangement, read_sources


def build():
    mech, fit, _, _, bom, _ = read_sources()
    geometry = arrangement(mech, fit)
    pieces = {piece["id"]: piece for piece in geometry["stock_pieces"]}
    bogies = geometry["bogies"]
    secondaries = [pad for bogie in bogies for pad in bogie["pads"] if pad["type"] == "secondary_top"]
    for pad in secondaries:
        upper, lower = pieces[pad["upper_piece"]], pieces[pad["piece"]]
        assert round(1000 * (upper["lower_m"][2] - lower["upper_m"][2]), 6) == pad["stock_face_gap_mm"]
        for i in (0, 1):
            assert round((upper["lower_m"][i] + upper["upper_m"][i]) / 2, 6) == pad["body_face_centre_m"][i]
    return {
        "body-bogie-mating.svg": drawing(geometry, pieces, mech["frame_revision"]),
        "body-bogie-limit-return.csv": return_form(bogies, bom, mech),
    }


def drawing(geometry, pieces, frame):
    bogie = geometry["bogies"][0]
    primary = [pad for pad in bogie["pads"] if pad["type"] == "primary_underside"]
    secondary = [pad for pad in bogie["pads"] if pad["type"] == "secondary_top"]
    sample = secondary[-1]
    body = pieces[sample["upper_piece"]]
    body_size = [round(1000 * (hi - lo)) for lo, hi in zip(body["lower_m"], body["upper_m"], strict=True)]
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 710" role="img" aria-labelledby="title desc">',
        '<title id="title">Airport car body-to-bogie mating and seating datums</title>',
        '<desc id="desc">Dimensioned bogie-local plan, transverse pad section and an enlarged suspension stack detail.</desc>',
        '<style>text{font:14px sans-serif;fill:#183348}.h{font:bold 18px sans-serif}.title{font:bold 28px sans-serif}'
        '.small{font:12px sans-serif}.mono{font:12px monospace}path{fill:none;stroke:#3a5669}'
        '.axis{stroke:#708ba0;stroke-dasharray:4 3}.primary{fill:#dca566;stroke:#96520f}'
        '.bogie{fill:#9cc7ba;stroke:#235b54}.body{fill:#c6d4e5;stroke:#466279}'
        '.reserve{fill:none;stroke:#476b83;stroke-dasharray:5 3}rect,path{stroke-width:1.3}</style>',
        '<rect width="1200" height="710" fill="white"/>',
    ]

    def line(x0, y0, x1, y1, kind=""):
        svg.append(f'<path d="M{x0:g} {y0:g}L{x1:g} {y1:g}" class="{kind}"/>')

    def text(x, y, label, kind=""):
        svg.append(f'<text x="{x:g}" y="{y:g}" class="{kind}">{label}</text>')

    def box(x, y, w, h, kind):
        svg.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" class="{kind}"/>')

    def hdim(x0, x1, y, label):
        line(x0, y, x1, y)
        for x in (x0, x1):
            line(x, y - 5, x, y + 5)
        text((x0 + x1) / 2 - len(label) * 3.2, y - 7, label, "small")

    text(50, 45, "Baghdad Airport  /  Body-to-bogie mating and seating datums", "title")
    text(50, 75, "Straight installed stock  •  dimensions in mm  •  drill and joint details await release")
    text(50, 118, "Plan  /  one bogie, local x–y", "h")
    text(636, 118, "Section A–A  /  local x = 0, looking along +x", "h")
    scale, px, py = .14, 318, 330
    line(100, py, 530, py, "axis")
    line(px, 150, px, 520, "axis")
    text(px + 8, 157, "+y / A", "small")
    text(px + 14, 504, "A", "small")
    text(506, py - 8, "+x", "small")
    lo, hi = bogie["installed_box_vehicle_m"]
    box(px - (hi[0] - lo[0]) * 500 * scale, py - (hi[1] - lo[1]) * 500 * scale,
        (hi[0] - lo[0]) * 1000 * scale, (hi[1] - lo[1]) * 1000 * scale, "reserve")
    for pad in primary + secondary:
        x, y, _ = pad["local_face_centre_mm"]
        w, h, _ = pad["pad_xyz_mm"]
        xx, yy = px + x * scale, py - y * scale
        box(xx - w * scale / 2, yy - h * scale / 2, w * scale, h * scale,
            "primary" if pad in primary else "bogie")
        line(xx - 4, yy, xx + 4, yy)
        line(xx, yy - 4, xx, yy + 4)
    axle0, axle1 = bogie["local_axle_planes_x_mm"]
    for axle in (axle0, axle1):
        x = px + scale * axle
        line(x, 170, x, 499, "axis")
    hdim(px + scale * axle0, px + scale * axle1, 533, f"{axle1 - axle0:g} axle planes")
    text(50, 567, "Primary pad centres  •  x ±1050  /  y ±1040", "small")
    text(50, 586, "Secondary pad centres  •  x 0  /  y ±850", "small")
    text(50, 605, "Crosses locate stock centres. Drilled hole patterns are open.", "small")

    sc, cx, rail = .20, 910, 318
    line(675, rail, 1145, rail, "axis")
    text(1075, rail + 17, "Railhead z = 0", "small")
    line(cx, 141, cx, rail + 10, "axis")
    for pad in secondary:
        _, y, z = pad["local_face_centre_mm"]
        # Orientation looking along +x places +y to the left.
        yy = cx - y * sc
        top = pad["upper_face_z_mm"]
        low_width = pad["pad_xyz_mm"][1]
        box(yy - body_size[1] * sc / 2, rail - (top + body_size[2]) * sc,
            body_size[1] * sc, body_size[2] * sc, "body")
        box(yy - low_width * sc / 2, rail - z * sc,
            low_width * sc, pad["pad_xyz_mm"][2] * sc, "bogie")
    centre_distance = secondary[-1]["local_face_centre_mm"][1] - secondary[0]["local_face_centre_mm"][1]
    hdim(cx - centre_distance * sc / 2, cx + centre_distance * sc / 2, 265,
         f"{centre_distance:g} secondary seat centres")
    text(732, 150, "+y", "small")

    x, y, zscale = 755, 483, .65
    top_z = sample["upper_face_z_mm"]
    lower_z = sample["local_face_centre_mm"][2]
    gap = sample["stock_face_gap_mm"]
    low_length, low_width, low_thickness = sample["pad_xyz_mm"]
    text(636, 358, "Detail B  /  one secondary stack, enlarged", "h")
    box(x - body_size[1] * zscale / 2, y - (gap + body_size[2]) * zscale,
        body_size[1] * zscale, body_size[2] * zscale, "body")
    box(x - low_width * zscale / 2, y, low_width * zscale, low_thickness * zscale, "bogie")
    line(x, y - gap * zscale - 22, x, y + 39, "axis")
    for yy in (y, y - gap * zscale):
        line(815, yy, 850, yy)
    line(842, y - gap * zscale, 842, y)
    text(852, y - gap * zscale / 2, f"{gap:g} full stack", "small")
    text(925, y - gap * zscale + 6, f"Body face z +{top_z:g}  •  {' × '.join(map(str, body_size))}", "small")
    text(925, y + 5, f"Bogie face z +{lower_z:g}  •  {low_length:g} × {low_width:g} × {low_thickness:g}", "small")
    text(716, 556, "Plate dimensions are x × y × thickness.", "small")
    w, h, t = primary[0]["pad_xyz_mm"]
    zp = primary[0]["local_face_centre_mm"][2]
    text(636, 586, f"Primary underside face z +{zp:g}  •  plate {w:g} × {h:g} × {t:g}", "small")
    text(636, 605, "Spring, shims, isolator, retention and fasteners require supplier detail.", "small")
    text(50, 657, "Frame " + frame, "mono")
    text(50, 681, "Stock drawing for supplier fit and inspection planning. No drilling centres, torque or load acceptance values assigned.", "small")
    return "\n".join(svg + ["</svg>", ""])


def return_form(bogies, bom, mech):
    buf = io.StringIO(newline="")
    writer = csv.writer(buf, lineterminator="\n")
    bidder = ["article_serial", "supplier_drawing_revision", "proposed_limit", "approved_limit", "unit",
              "governing_pose_and_load", "measured_value", "measurement_uncertainty", "signed_margin",
              "measurement_method_and_calibration", "evidence_reference", "reviewer_signature_and_date"]
    writer.writerow(["candidate_id", "frame_revision", "item", "datum_or_stock_basis", "return_scope", *bidder])
    identity = [mech["candidate_id"], mech["frame_revision"]]

    def row(item, basis, scope):
        writer.writerow([*identity, item, basis, scope, *([""] * len(bidder))])

    for bogie in bogies:
        name = bogie["assembly"]
        for pad in bogie["pads"]:
            location = "car xyz m " + " / ".join(map(str, pad["body_face_centre_m"]))
            if pad["type"] == "secondary_top":
                basis = f'{location}; paired body plate {pad["upper_piece"]}; 156 mm nominal stock gap'
                scope = "Report paired face gap and each plane survey, loaded stack, residual jounce/rebound and retention; separate records by pose and metric"
            else:
                basis = location + "; nominal primary underside face"
                scope = "Report paired axlebox fit, guide position, face flatness and location, jounce/rebound and stop clearance; separate records by pose and metric"
            row(name + "/" + pad["piece"], basis, scope)
        row(name + " hole patterns and joints", "Primary and secondary pad stock faces in controlled vehicle frame",
            "Attach whole mating pattern and fit specification with stackup; return hole type, fit and position, grip, clearance, tightening, weld/attachment inspection and allowable load evidence")
        row(name + " off-axis loads and retention", "Supplied mount, stops, torque reactions and bogie-to-body retention",
            "Return compatible load cases, direction, joint capacity, fatigue assessment, travel restraint and fastener/inspection access")
    joint_names = (
        "Chord splice", "Post-end joint", "Crossmember-end joint", "Brace-end connection",
        "Transom and saddle ends", "Primary and secondary pad attachments",
    )
    for source in bom:
        if source["item"] in joint_names:
            row(source["item"], source["per_car"] + " per car; controlled piece and interface drawings",
                "Identify each joint and process; return approved joint prep, visual/NDT inspection results, inspection access and governing release criteria")
    return buf.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for name, data in build().items():
        target = HERE / name
        if args.check:
            if not target.exists() or target.read_bytes() != data.encode():
                parser.exit(1, f"Stale body-to-bogie draft: {target}\n")
        else:
            target.write_bytes(data.encode())


if __name__ == "__main__":
    main()
