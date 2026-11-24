"""Render the two-terminal viaduct logistics concept and local CAD envelopes."""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle

HERE = Path(__file__).resolve().parent
SPAN, WIDTH, DEPTH, PITCH = 20., 4., 1.55, 4.5
WEB, SLAB = .20, .24
SOFFIT = 6.
RAIL_OFFSET = .675
BG = "#f7fafc"
INK = "#172e41"
MUTED = "#455f72"
DECK = "#8ca2b3"
TEAL = "#087d7a"
ORANGE = "#c26732"
PALE = "#dae4ec"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "text.color": INK,
    "figure.facecolor": BG, "axes.facecolor": BG,
})


def box(ax, x, y, w, h, color=DECK, **style):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=color, **style))


def arrow(ax, start, end, color=TEAL, mode="-|>", width=2.2):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=mode, mutation_scale=15,
                                 color=color, lw=width, shrinkA=0, shrinkB=0))


def label(ax, x, y, text, color=INK, *, bold=False, align="center", size=10):
    ax.text(x, y, text, va="center", ha=align, color=color, fontsize=size,
            weight="bold" if bold else "normal")


def illustration(title, subtitle, footer, *, height=5.1):
    fig = plt.figure(figsize=(10.7, height), dpi=125)
    fig.text(.047, .939, title, weight="bold", size=22)
    fig.text(.049, .887, subtitle, size=11, color=MUTED)
    fig.text(.049, .045, footer, size=9, color=MUTED)
    return fig


def two_fronts(path):
    fig = illustration(
        "Build the viaduct from both ends",
        "Compare deck delivery with repeated road deliveries on the same double-track corridor",
        "Concept sequence · Starter mobilisation, centre closure and exceptional obstructions retain separate access plans.",
    )
    ax = fig.add_axes((.05, .15, .9, .69), xlim=(0, 100), ylim=(0, 68))
    ax.axis("off")
    label(ax, 1, 64, "RAIL-FED FROM TWO TERMINALS", TEAL, bold=True, align="left")
    for x in [17, 24, 31, 38, 45, 55, 62, 69, 76, 83]:
        ax.plot([x, x], [37, 43], color=PALE, lw=3)
    for y in (42, 46):
        ax.plot([13, 87], [y, y], color=PALE, lw=4)
        ax.plot([13, 40], [y, y], color=TEAL, lw=3)
        ax.plot([60, 87], [y, y], color=TEAL, lw=3)
    for x in (1, 87):
        box(ax, x, 38, 12, 12, "#d8eee9", edgecolor=TEAL, linewidth=1.5)
        label(ax, x + 6, 44, "Precast\nyard", TEAL, bold=True, size=9)
    for x in [35, 59]:
        box(ax, x, 40, 6, 9, "#a3cbc8", edgecolor=TEAL, linewidth=1.2)
    for x in [21, 72]:
        box(ax, x, 45.1, 6, 2.8, ORANGE)
    label(ax, 20, 33, "Two starter bays", MUTED, size=9)
    label(ax, 80, 33, "Two starter bays", MUTED, size=9)
    label(ax, 25, 53, "Flatbed feed", ORANGE, size=9)
    label(ax, 75, 53, "Flatbed feed", ORANGE, size=9)
    arrow(ax, (35, 55), (45, 55))
    arrow(ax, (65, 55), (55, 55))
    label(ax, 50, 32, "Midline closure bay", MUTED, size=9)
    ax.plot([50, 50], [35, 49], color=MUTED, linestyle=(0, (2, 3)), lw=1)
    ax.plot([1, 99], [27, 27], color=PALE, lw=1)
    label(ax, 1, 21, "ROAD-FED MOBILE CRANES", ORANGE, bold=True, align="left")
    ax.plot([3, 96], [11, 11], color=PALE, lw=7)
    for x in (23, 43, 63, 83):
        box(ax, x, 9.4, 5, 3.2, ORANGE)
    for x in (34, 68):
        ax.plot([x, x + 4], [7, 15.5], color=MUTED, lw=2)
        ax.plot([x + 4, x + 4], [15.5, 12.5], color=MUTED, lw=.8)
    label(ax, 50, 4, "Street delivery and lift windows repeat along the route", MUTED, size=9)
    fig.savefig(path, dpi=125)
    plt.close(fig)


def u_profile(center, z=SOFFIT):
    """Outline of the nominal unthickened girder section in transverse Y/Z."""
    left, right = center - WIDTH / 2, center + WIDTH / 2
    return [(left, z), (right, z), (right, z + DEPTH),
            (right - WEB, z + DEPTH), (right - WEB, z + SLAB),
            (left + WEB, z + SLAB), (left + WEB, z + DEPTH), (left, z + DEPTH)]


def launch_section(path):
    fig = illustration(
        "Move beams on the released deck",
        "20 m shared-pier trial geometry · Local gantry and feed envelopes are indicative",
        "The concept leaves track support, launch reactions, suspended loads and exclusion zones to engineered temporary works.",
        height=5.35,
    )
    side = fig.add_axes((.05, .177, .53, .64), xlim=(-43, 33), ylim=(-1.55, 17))
    cross = fig.add_axes((.61, .177, .34, .64), xlim=(-7, 7), ylim=(-1.55, 17))
    side.axis("off")
    cross.axis("off")
    for ax, bounds in [(side, (-42, 32)), (cross, (-6.7, 6.7))]:
        ax.plot(bounds, [0, 0], color=MUTED, lw=1)
    label(side, -41, 16, "ALONG THE ROUTE", bold=True, align="left")
    label(cross, -6.6, 16, "ACROSS THE DECK", bold=True, align="left")
    for x in [-40, -20, 0, 20]:
        box(side, x - 1, .2, 2, 5.8, DECK)
        box(side, x - 2, -.4, 4, .7, PALE)
    for x in [-40, -20]:
        box(side, x, SOFFIT, SPAN - .4, SLAB)
        box(side, x, SOFFIT + SLAB, SPAN - .4, DEPTH - SLAB, PALE, alpha=.55)
    box(side, 0, SOFFIT, SPAN, DEPTH, "none", edgecolor=ORANGE, linestyle="--", lw=1.2)
    side.plot([-40, 0], [SOFFIT + .4, SOFFIT + .4], color=TEAL, lw=1.4, zorder=4)
    box(side, -34, 6.52, 22, .55, INK)
    box(side, -33, 7.07, SPAN, DEPTH, ORANGE)
    label(side, -24, 11., "Girder on flatbed", ORANGE, size=10)
    arrow(side, (-17, 10.1), (-6, 10.1))
    box(side, -15, 13.15, 43, 1.15, TEAL)
    for x in [-12, 18]:
        box(side, x, 7.6, 1.4, 5.55, TEAL, alpha=.75)
    label(side, 7, 12.2, "Launching gantry", TEAL, size=10)
    label(side, -22, 4.65, "Released bays (cutaway)", MUTED, size=10)
    label(side, 10, 4.65, "Next bay", ORANGE, size=10)
    arrow(side, (0, 1.65), (20, 1.65), ORANGE, "<->", 1.1)
    label(side, 10, 2.45, "20 m", ORANGE, size=9)
    for x in [-20, 0, 20]:
        side.plot([x, x], [0.5, 1.75], color=MUTED, lw=.65)
    label(side, -39, -1, "Pier and foundation access", MUTED, align="left", size=8.7)

    box(cross, -1.0, .25, 2.0, 5.0)
    box(cross, -5.0, 5.25, 10, .75)
    box(cross, -2.0, -.4, 4, .65, PALE)
    for center in (-PITCH / 2, PITCH / 2):
        cross.add_patch(Polygon(u_profile(center), closed=True, facecolor=DECK, edgecolor=MUTED, lw=.8))
    feed_center = -PITCH / 2
    for x in [feed_center - RAIL_OFFSET, feed_center + RAIL_OFFSET]:
        box(cross, x - .08, 6.32, .16, .12, TEAL)
    box(cross, feed_center - 1.2, 6.51, 2.4, .55, INK)
    cross.add_patch(Polygon(u_profile(feed_center, 7.09), closed=True, facecolor=ORANGE, edgecolor=ORANGE))
    box(cross, -5.8, 13.15, 11.6, 1.15, TEAL)
    for x in [-5.7, 5.25]:
        box(cross, x, 6.25, .45, 6.9, TEAL, alpha=.75)
    arrow(cross, (-2.25, 10.75), (2.25, 10.75), ORANGE, "<->", 1.5)
    label(cross, 0, 11.55, "Transverse placement", ORANGE, size=9)
    label(cross, 0, 4.5, "Shared crosshead", MUTED, size=10)
    arrow(cross, (-2.25, 2.8), (2.25, 2.8), MUTED, "<->", 1.1)
    label(cross, 0, 1.85, "4.5 m track pitch", MUTED, size=9)
    label(cross, 0, -1, "Clearance to verify across both decks", MUTED, size=8.7)
    fig.savefig(path, dpi=125)
    plt.close(fig)


class Mesh:
    def __init__(self):
        self.lines = [
            "# OSR rail-fed erection concept; coordinates in metres",
            "# Illustrative envelopes only; no fabrication or lifting geometry",
        ]
        self.vertices = 0

    def extrusion(self, name, x0, x1, yz):
        self.lines.append(f"o {name}")
        self.lines.append(f"g {name}")
        begin = self.vertices + 1
        n = len(yz)
        for x in (x0, x1):
            self.lines.extend(f"v {x:.3f} {y:.3f} {z:.3f}" for y, z in yz)
        a = list(range(begin, begin + n))
        b = list(range(begin + n, begin + 2 * n))
        self.lines.append("f " + " ".join(map(str, reversed(a))))
        self.lines.append("f " + " ".join(map(str, b)))
        for i in range(n):
            j = (i + 1) % n
            self.lines.append(f"f {a[i]} {a[j]} {b[j]} {b[i]}")
        self.vertices += 2 * n

    def block(self, name, x0, x1, y0, y1, z0, z1):
        self.extrusion(name, x0, x1, [(y0, z0), (y1, z0), (y1, z1), (y0, z1)])


def model(path):
    mesh = Mesh()
    for index, x in enumerate([-40., -20., 0., 20.]):
        mesh.block(f"foundation_envelope_{index}", x - 2, x + 2, -2., 2., -.4, .25)
        mesh.block(f"pier_envelope_{index}", x - .95, x + .95, -1., 1., .25, 5.25)
        mesh.block(f"shared_crosshead_{index}", x - 1.4, x + 1.4, -5., 5., 5.25, SOFFIT)
    for track, center in enumerate([-PITCH / 2, PITCH / 2]):
        for index, x in enumerate([-40., -20.]):
            profile = u_profile(center)
            left, bottom = profile[0]
            right, _ = profile[1]
            top = SOFFIT + DEPTH
            # The three separate prisms keep a void and avoid relying on a
            # faceted importer triangulating a concave end cap.
            name = f"released_track{track}_bay{index}"
            mesh.block(name + "_floor", x, x + 19.8, left, right, bottom, bottom + SLAB)
            mesh.block(name + "_webL", x, x + 19.8, left, left + WEB, bottom + SLAB, top)
            mesh.block(name + "_webR", x, x + 19.8, right - WEB, right, bottom + SLAB, top)
    q = -PITCH / 2
    for side, y in enumerate([q - RAIL_OFFSET, q + RAIL_OFFSET]):
        mesh.block(f"temporary_service_rail_{side}", -39., -.5, y - .08, y + .08, 6.33, 6.45)
    mesh.block("transport_flatbed_envelope", -34., -12., q - 1.2, q + 1.2, 6.52, 7.07)
    for index, x in enumerate([-32., -14.]):
        mesh.block(f"transport_rail_bogie_envelope_{index}", x - .5, x + .5,
                   q - .82, q + .82, 6.45, 6.52)
    mesh.block("carried_girder_floor", -33., -13., q - WIDTH / 2, q + WIDTH / 2, 7.07, 7.07 + SLAB)
    for side, y in enumerate([q - WIDTH / 2, q + WIDTH / 2 - WEB]):
        mesh.block(f"carried_girder_web_{side}", -33., -13., y, y + WEB, 7.07 + SLAB, 7.07 + DEPTH)
    for side, y in enumerate([-5.3, 5.3]):
        mesh.block(f"gantry_longitudinal_envelope_{side}", -15., 28., y - .35, y + .35, 13.15, 14.30)
        for index, x in enumerate([-11., 19.]):
            mesh.block(f"gantry_support_envelope_{side}_{index}", x - .40, x + .40,
                       y - .35, y + .35, 6., 13.15)
    for index, x in enumerate([-3., 16.]):
        mesh.block(f"gantry_transverse_envelope_{index}", x - .45, x + .45, -5.65, 5.65, 12.9, 14.2)
    for track, center in enumerate([-PITCH / 2, PITCH / 2]):
        for edge, y in enumerate([center - WIDTH / 2, center + WIDTH / 2]):
            mesh.block(f"empty_bay_reference_edge_{track}_{edge}", 0., SPAN, y - .02, y + .02, SOFFIT, SOFFIT + .02)
    path.write_text("\n".join(mesh.lines) + "\n", encoding="ascii")


def dxf(path):
    """Write a small model-space DXF with an elevation and a cross section."""
    records = []

    def add(*pairs):
        records.extend(f"{code}\n{value}" for code, value in pairs)

    add((0, "SECTION"), (2, "HEADER"), (9, "$ACADVER"), (1, "AC1015"),
        (9, "$INSUNITS"), (70, 6), (0, "ENDSEC"))
    add((0, "SECTION"), (2, "TABLES"), (0, "TABLE"), (2, "LAYER"), (70, 7))
    layers = {"ground": 8, "pier": 9, "girder": 9, "feed": 4, "gantry": 3, "target": 30, "labels": 7}
    for key, color in layers.items():
        add((0, "LAYER"), (2, key), (70, 0), (62, color), (6, "CONTINUOUS"))
    add((0, "ENDTAB"), (0, "ENDSEC"), (0, "SECTION"), (2, "ENTITIES"))

    def line(a, b, layer):
        add((0, "LINE"), (8, layer), (10, a[0]), (20, a[1]),
            (30, 0), (11, b[0]), (21, b[1]), (31, 0))

    def contour(points, layer):
        for first, second in zip(points, [*points[1:], points[0]], strict=True):
            line(first, second, layer)

    def block(x0, x1, z0, z1, layer):
        contour([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], layer)

    def mark(x, z, caption):
        add((0, "TEXT"), (8, "labels"), (10, x), (20, z), (30, 0),
            (40, .38), (1, caption))

    line((-42., 0), (32., 0), "ground")
    for x in (-40., -20., 0., 20.):
        block(x - 2., x + 2., -.4, .25, "pier")
        block(x - .95, x + .95, .25, 5.25, "pier")
        block(x - 1.4, x + 1.4, 5.25, SOFFIT, "pier")
    for x in (-40., -20.):
        block(x, x + 19.8, SOFFIT, SOFFIT + DEPTH, "girder")
    block(-39., -.5, 6.33, 6.45, "feed")
    block(-34., -12., 6.52, 7.07, "feed")
    block(-33., -13., 7.07, 7.07 + DEPTH, "feed")
    block(-15., 28., 13.15, 14.30, "gantry")
    block(0., SPAN, SOFFIT, SOFFIT + DEPTH, "target")
    mark(-40., 15.30, "ALONG ROUTE / metre units")
    mark(-39., 9.95, "flatbed and carried girder")
    mark(.5, 3.5, "20 m nominal advance")
    # Transverse view is translated 47 m in model space for presentation.
    offset = 47.
    line((offset - 6.7, 0), (offset + 6.7, 0), "ground")
    block(offset - 1., offset + 1., .25, 5.25, "pier")
    block(offset - 5., offset + 5., 5.25, SOFFIT, "pier")
    for center in (-PITCH / 2, PITCH / 2):
        contour(u_profile(offset + center), "girder")
    contour(u_profile(offset - PITCH / 2, 7.07), "feed")
    block(offset - 5.8, offset + 5.8, 13.15, 14.30, "gantry")
    mark(offset - 6.7, 15.30, "ACROSS DECK / 4.5 m track pitch")
    mark(offset - 6.7, -1.5, "Concept envelopes, engineering checks pending")
    add((0, "ENDSEC"), (0, "EOF"))
    path.write_text("\n".join(records) + "\n", encoding="ascii")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=True, parents=True)
    two_fronts(args.output / "two-fronts.png")
    launch_section(args.output / "launch-section.png")
    model(args.output / "rail-fed-launch.obj")
    dxf(args.output / "rail-fed-launch.dxf")


if __name__ == "__main__":
    main()
