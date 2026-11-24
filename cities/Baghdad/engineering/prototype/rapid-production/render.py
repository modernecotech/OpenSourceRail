"""Render the rapid manufacturing concept and export its editable envelopes."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
# Dimensions in metres. The body and bogie beds are specified by
# vehicle-resources.toml. Other boxes show representative factory zoning.
BOXES = (
    ("chassis_body_bed", 1.0, 1.1, 0.0, 18.0, 3.2, .55, "#0f766e"),
    ("bogie_frame_bed", 16.6, 6.8, 0.0, 3.2, 2.5, .60, "#2865a6"),
    ("stock_infeed", 1.0, 9.5, 0.0, 12.5, 1.0, .40, "#55657c"),
    ("standard_tube_laser", 4.8, 6.8, 0.0, 5.5, 2.3, 2.20, "#c36d21"),
    ("stock_saw_preparation", 11.6, 6.8, 0.0, 3.6, 2.3, 1.20, "#55657c"),
    ("post_join_gauging", 21.1, 1.1, 0.0, 3.0, 3.2, .40, "#2865a6"),
)
NAMES = {
    "chassis_body_bed": "18 × 3.2 m body jig",
    "bogie_frame_bed": "Bogie jig\n3.2 × 2.5 m",
    "stock_infeed": "Stock receiving and kitting",
    "standard_tube_laser": "Tube laser\nbooking",
    "stock_saw_preparation": "Heavy stock\nsaw / prep",
    "post_join_gauging": "Gauge and\ninspect",
}
METHODS = ("saw_fixture", "shared_cnc", "dedicated")
COLORS = ("#55657c", "#0f766e", "#c36d21")
LABELS = ("Saw + manual fixtures", "Shared CNC + fixtures", "Dedicated laser + robots")


def export_geometry():
    obj = ["# OSR rapid steel manufacturing envelopes in metres"]
    dxf = ["0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1015",
           "9", "$INSUNITS", "70", "6", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    for i, (name, x, y, z, width, depth, height, _) in enumerate(BOXES, start=0):
        corners = [(x, y), (x + width, y), (x + width, y + depth), (x, y + depth)]
        obj.append(f"o {name}")
        for level in (z, z + height):
            obj.extend(f"v {px:.5f} {py:.5f} {level:.5f}" for px, py in corners)
        faces = ((1, 4, 3, 2), (5, 6, 7, 8), (1, 2, 6, 5), (2, 3, 7, 6), (3, 4, 8, 7), (4, 1, 5, 8))
        obj.extend("f " + " ".join(str(i * 8 + index) for index in face) for face in faces)
        dxf += ["0", "LWPOLYLINE", "5", f"{i + 256:X}", "100", "AcDbEntity", "8", name,
                "100", "AcDbPolyline", "90", "4", "70", "1"]
        for px, py in corners:
            dxf += ["10", f"{px:.5f}", "20", f"{py:.5f}"]
    dxf += ["0", "ENDSEC", "0", "EOF"]
    (HERE / "workcell-envelopes.obj").write_text("\n".join(obj) + "\n")
    (HERE / "workcell-plan.dxf").write_text("\n".join(dxf) + "\n")


def render():
    result = json.loads((HERE / "comparison.json").read_text())
    fig = plt.figure(figsize=(15, 8.6), facecolor="#f2f6f8")
    fig.text(.045, .91, "Rapid manufacture of steel body and bogie frames", fontsize=24,
             fontweight="bold", color="#0d2237")
    fig.text(.045, .872, "Modular fixtures retain local fabrication capability while shared CNC handles compatible stock.",
             fontsize=13, color="#384e62")
    grid = fig.add_gridspec(2, 2, left=.045, right=.965, top=.82, bottom=.12,
                            hspace=.32, wspace=.32, height_ratios=(1.5, 1))
    ax = fig.add_subplot(grid[0, :])
    ax.set_aspect("equal")
    ax.set_xlim(0, 24.9)
    ax.set_ylim(.3, 11)
    ax.axis("off")
    ax.add_patch(Rectangle((.25, .55), 24.35, 10.2, fc="#ffffff", ec="#c9d5de", lw=1.2))
    for name, x, y, _, w, d, _, color in BOXES:
        ax.add_patch(Rectangle((x, y), w, d, ec=color, fc=color, alpha=.93))
        ax.text(x + w / 2, y + d / 2, NAMES[name], color="white", fontsize=9.5,
                ha="center", va="center", fontweight="semibold")
    for start, end in (((13.7, 6.7), (13.7, 4.42)), ((7.6, 6.7), (7.6, 4.42)),
                       ((19.1, 2.75), (20.9, 2.75)), ((18.2, 6.7), (21.1, 4.38))):
        ax.annotate("", xy=end, xytext=start,
                    arrowprops={"arrowstyle": "-|>", "color": "#4d6577", "lw": 1.4})
    ax.text(20.25, 10.12, "Plan view · concept zoning", ha="center", va="center",
            fontsize=11, color="#384e62", fontweight="semibold")

    def annotate(ax, key, title, subtext, fmt, limit):
        ax.set_facecolor("#f2f6f8")
        ax.set_title(title, loc="left", color="#0d2237", fontsize=14, fontweight="bold", pad=18)
        ax.text(0, 1.015, subtext, transform=ax.transAxes, fontsize=10, color="#384e62")
        values = [key(method) for method in METHODS]
        bars = ax.barh(LABELS, values, color=COLORS, height=.52)
        ax.bar_label(bars, labels=[fmt.format(v) for v in values], padding=6, fontsize=10,
                     color="#0d2237", fontweight="bold")
        for bar, label in zip(bars, LABELS, strict=True):
            ax.text(limit * .02, bar.get_y() + bar.get_height() / 2, label,
                    ha="left", va="center", fontsize=10, color="white", fontweight="semibold")
        ax.set_xlim(0, limit)
        ax.invert_yaxis()
        ax.spines[:].set_visible(False)
        ax.tick_params(axis="both", length=0, labelcolor="#384e62")
        ax.tick_params(axis="y", labelleft=False)
        ax.tick_params(axis="x", labelbottom=False)
        ax.set_axisbelow(True)
        ax.grid(axis="x", color="#ccd8df", lw=.6)

    annotate(fig.add_subplot(grid[1, 0]),
             lambda m: result["orders"]["36"][m]["last_coated_frame_set_shift_days"],
             "Delivery of 36 frame sets", "Last coated frame set, staffed shift days", "{:.1f}", 280)
    annotate(fig.add_subplot(grid[1, 1]),
             lambda m: result["orders"]["180"][m]["price_cases"]["base"]["usd_per_car"],
             "Cost at 180 frame sets", "Selected fabrication steps, base USD per car", "${:,.0f}", 39000)
    fig.text(.045, .04, "OpenSourceRail  /  Approximate work envelopes and modeled rates. "
             "Frame joining, inspection and equipment capacity require supplier demonstration.",
             fontsize=10, color="#384e62")
    fig.savefig(HERE / "workcells.png", dpi=145)
    plt.close(fig)


if __name__ == "__main__":
    export_geometry()
    render()
