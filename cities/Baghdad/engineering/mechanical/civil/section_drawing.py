"""Generate cross-sections at a common transverse datum from the quotation inputs."""
from pathlib import Path
import argparse
import tomllib

from develop_civil import CITY, DIR, PARENT, evaluate


def drawing():
    result = evaluate()
    settings = tomllib.loads((DIR/"concept.toml").read_text())
    system = tomllib.loads((CITY/"system.toml").read_text())
    p, b = settings["platform"], settings["box"]
    station = system["station_geometry"]
    rig = tomllib.loads((PARENT/"quotation.toml").read_text())
    edge = station["island_width_m"]/2
    track = station["straight_track_centre_spacing_m"]/2
    col = rig["platform"]["bent_column_lateral_m"]
    box, panel = result["track"], result["platform"]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 680" role="img"><title>Baghdad straight station and 10 m box, quotation sections</title><style>text{font:15px sans-serif;fill:#173545}.title{font:bold 23px sans-serif}.note{font:13px sans-serif}.slab{fill:#ccd8dd;stroke:#344f5d}.head{fill:#acbec6;stroke:#344f5d}.dim{fill:none;stroke:#46636b}.axis{stroke:#917222;stroke-dasharray:5 4}</style><rect width="1100" height="680" fill="white"/>']
    def text(x,y,label,cls=""):
        parts.append(f'<text x="{x}" y="{y}" class="{cls}">{label}</text>')
    def rect(x,y,w,h,cls):
        parts.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" class="{cls}"/>')
    def line(x,y,X,Y,cls):
        parts.append(f'<path class="{cls}" d="M{x:g} {y:g}L{X:g} {Y:g}"/>')
    text(32,37,"Baghdad · straight island and independent track beams","title")
    text(32,66,"Transverse view looking along track. Rail-head datum z = 0. Dimensions in metres.")
    scale = 59
    def X(y):
        return 550+scale*y
    for sign in (-1,1):
        x=X(sign*track)
        rect(x-scale*b["width_m"]/2,182,scale*b["width_m"],scale*b["depth_m"],"slab")
        rect(x-scale*(b["width_m"]/2-b["web_m"]),182+scale*b["slab_m"],
             scale*(b["width_m"]-2*b["web_m"]),scale*(b["depth_m"]-2*b["slab_m"]),"head")
        line(x,100,x,287,"axis")
        xcol = X(sign*col)
        rect(xcol-8,185,16,82,"head")
        contact=sign*(track+system["vehicle_geometry"]["contact_rail_outboard_offset_m"])
        line(X(contact),145,X(contact),245,"axis")
        text(X(contact)-34,137,f"y {contact:+.3f}")
        text(x-43,306,f"Track {sign*track:+.3f}")
    rect(X(-edge),154,2*edge*scale,p["head_depth_m"]*scale,"head")
    pitch=station["island_width_m"]/p["panels_across"]
    for i in range(p["panels_across"]):
        rect(X(-edge+i*pitch+p["panel_joint_m"]/2),154-p["panel_thickness_m"]*scale,
             panel["panel_width_m"]*scale,p["panel_thickness_m"]*scale,"slab")
    text(X(-edge),122,f"Platform edge −{edge:.2f}");text(X(edge)-56,122,f"+{edge:.2f}")
    text(429,238,f"Column axes at ±{col:.2f}");text(447,266,"Deck surface z = +1.00")
    text(32,336,"Outer dashed axes mark protected conductor datums. Rail seats, conductor brackets and column widths await detailing.","note")
    line(32,350,1068,350,"dim")
    text(32,386,"Track box at midspan","title")
    text(536,386,"Island panel and bent","title")
    s=135
    rect(66,426,b["width_m"]*s,b["depth_m"]*s,"slab")
    parts.append(f'<rect x="{66+b["web_m"]*s}" y="{426+b["slab_m"]*s}" width="{(b["width_m"]-2*b["web_m"])*s}" height="{(b["depth_m"]-2*b["slab_m"])*s}" fill="white" stroke="#344f5d"/>')
    text(66,416,f'{b["width_m"]:.2f} overall × {b["depth_m"]:.2f} deep')
    text(108,488,f'{b["web_m"]:.2f} side webs');text(108,521,f'{b["slab_m"]:.2f} flanges')
    text(32,647,f'{box["length_m"]:g} m stock · {box["bearing_span_m"]:g} m seat spacing · {b["solid_end_m"]:.2f} m solid ends')
    text(536,425,f'{p["panels_across"]} precast panels across each 5 m platform bay')
    text(536,463,f'{panel["panel_length_m"]:.2f} × {panel["panel_width_m"]:.2f} × {p["panel_thickness_m"]:.2f} per panel')
    text(536,501,f'{p["panel_joint_m"]*1000:.0f} mm panel joints · {panel["panel_support_span_m"]:.2f} m between seat centres')
    text(536,539,f'{2*edge:g} × {p["head_width_m"]:.2f} × {p["head_depth_m"]:.2f} m transverse head')
    text(536,577,f'{result["platform"]["centre_drain_drop_m"]*1000:.0f} mm finished-surface fall to centre drain')
    text(536,615,"End bays, stair openings and equipment bays require separate frames.")
    text(536,650,"Prototype quotation · section and support elevations schematic","note")
    return "\n".join(parts+["</svg>"])+"\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = DIR/"station-and-box.svg"
    if args.check:
        if drawing() != path.read_text():
            raise SystemExit("Stale civil drawing")
    else:
        path.write_text(drawing())
