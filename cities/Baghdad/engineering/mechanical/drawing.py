"""Dimensioned quotation-jig plan from the same mechanical input as the schedule."""
from xml.etree.ElementTree import Element, SubElement, indent, tostring


def drawing(geometry, rig):
    svg = Element("svg", {"xmlns": "http://www.w3.org/2000/svg",
                          "viewBox": "0 0 1040 615", "role": "img",
                          "aria-labelledby": "title desc"})
    SubElement(svg, "title", id="title").text = "Baghdad bogie jig and sidewall coordination plan"
    SubElement(svg, "desc", id="desc").text = (
        "Plan views with local x forward and y left. The outer car door sits over a "
        "bogie pivot. Two bogie axle planes, four primary suspension seats and two "
        "secondary seats are shown at quotation coordinates.")
    def node(tag, **args):
        return SubElement(svg, tag, {k.replace("_", "-"): str(v) for k, v in args.items()})

    def label(x, y, s, size=14, weight=400, colour="#20333c"):
        node("text", x=x, y=y, font_size=size, font_weight=weight, fill=colour,
             font_family="sans-serif").text = s

    def line(x1, y1, x2, y2, colour="#445866", width=1, dash=None):
        attrs = dict(x1=x1, y1=y1, x2=x2, y2=y2, stroke=colour, stroke_width=width)
        if dash:
            attrs["stroke_dasharray"] = dash
        node("line", **attrs)

    def rect(x, y, w, h, fill, stroke="#27495c", width=1):
        node("rect", x=x, y=y, width=w, height=h, fill=fill, stroke=stroke, stroke_width=width)

    rect(0, 0, 1040, 615, "#ffffff", "none")
    label(42, 42, "Baghdad   /   Powered bogie and carbody interfaces", 26, 650)
    label(42, 68, "First-programme quotation study   •   Plan views   •   Dimensions in metres")
    # Longitudinal car plan. Lines denote interfaces, not finished profiles.
    cx, cy, scale = 518, 159, 51
    length, width = geometry["car_body_length_m"], geometry["body_width_m"]
    top, bottom = cy - width*scale/2, cy + width*scale/2
    rect(cx-length*scale/2, top, length*scale, width*scale, "#f2f6f8")
    line(cx-length*scale/2, cy, cx+length*scale/2, cy, dash="7 4")
    for x in geometry["bogie_centres_m"]:
        px = cx+x*scale
        rect(px-rig["frame_length_m"]*scale/2, cy-rig["frame_width_m"]*scale/2,
             rig["frame_length_m"]*scale, rig["frame_width_m"]*scale, "#dce8e4", "#286c63")
        line(px, top-5, px, bottom+6, "#286c63", 2, "4 4")
        label(px-49, cy+5, f"pivot {x:+.2f}", 13, 600)
    for x in geometry["door_centres_m"]:
        px = cx+x*scale
        for edge in (top, bottom):
            half = geometry["door_clear_width_m"]*scale/2
            line(px-half, edge, px+half, edge, "#cb611d", 6)
    label(86, 254, f"Body {length:.2f} × {width:.2f}    |    Orange gaps represent clear openings of {geometry['door_clear_width_m']:.2f} on each side.")
    label(86, 278, "End doorway and bolster coincide along x. Keep the door threshold clear across the bolster.")
    line(42, 301, 998, 301, "#c7d0d5")
    # One frame assembly viewed at a larger scale.
    cx, cy, scale = 274, 449, 100
    label(42, 328, "One bogie in its own frame", 18, 650)
    frame_l, frame_w = rig["frame_length_m"], rig["frame_width_m"]
    rect(cx-frame_l*scale/2, cy-frame_w*scale/2, frame_l*scale, frame_w*scale,
         "#f2f6f8", "#286c63", 2)
    line(cx-frame_l*scale/2-12, cy, cx+frame_l*scale/2+12, cy, dash="5 3")
    for s in (-1, 1):
        px = cx + s*rig["wheelbase_m"]*scale/2
        line(px, cy-frame_w*scale/2, px, cy+frame_w*scale/2, "#426e91", 3)
        for t in (-1, 1):
            py = cy+t*rig["primary_seat_lateral_m"]*scale
            rect(px-5, py-5, 10, 10, "#286c63")
        node("circle", cx=cx, cy=cy+s*rig["secondary_seat_lateral_m"]*scale, r=6,
             fill="#cb611d")
    label(485, 365, f"Frame allowance   {frame_l:.2f} long × {frame_w:.2f} wide", 18, 650)
    label(485, 402, f"Two axle planes   x = ±{rig['wheelbase_m']/2:.2f}", 16, 500, "#426e91")
    label(485, 435, f"Four primary seats   x = ±{rig['wheelbase_m']/2:.2f}, y = ±{rig['primary_seat_lateral_m']:.2f}", 16, 500, "#286c63")
    label(485, 468, f"Two secondary seats   x = 0, y = ±{rig['secondary_seat_lateral_m']:.2f}", 16, 500, "#a44a12")
    label(485, 511, "x increases rightward. Positive y is upward on this sheet.")
    label(485, 537, "Motor, brake, wheel and tool envelopes require supplier CAD.")
    label(42, 592, "Assembly interface study   /   Shop sections, hole patterns, z-datums and loads require first-article design.", 14)
    indent(svg)
    return tostring(svg, encoding="unicode") + "\n"
