"""Render the Baghdad proposal from its single Markdown source and two GIS maps."""

from __future__ import annotations

import html
import json
import math
import gzip
from hashlib import sha256
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mistune
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "Baghdad-Metro-Proposal.pdf"
MAP_IMAGES = (HERE / "maps" / "Baghdad-148km.png", HERE / "maps" / "Baghdad-606km.png")
CITY_CONTEXT = ROOT / "cities/catalogue/west-asia/Iraq/Baghdad/map-context.json.gz"
CITY_CONTEXT_SHA256 = "21ab8f69f933ee84e32158f3b5de54d29d5fea8518183457856d2745e6c78168"
GITHUB = "https://github.com/modernecotech/OpenSourceRail/blob/main/"


def inline(nodes):
    out = []
    for node in nodes:
        kind = node["type"]
        if kind == "text":
            out.append(html.escape(node["raw"]))
        elif kind in ("strong", "emphasis"):
            tag = "b" if kind == "strong" else "i"
            out.append(f"<{tag}>{inline(node['children'])}</{tag}>")
        elif kind == "codespan":
            out.append(html.escape(node["raw"]))
        elif kind == "link":
            url = node["attrs"]["url"]
            if not url.startswith(("http://", "https://")):
                url = GITHUB + (HERE / url).resolve().relative_to(ROOT).as_posix()
            out.append(f'<link href="{html.escape(url, quote=True)}">{inline(node["children"])}</link>')
        elif "children" in node:
            out.append(inline(node["children"]))
    return "".join(out)


def map_images():
    """Publish legible, source-bound planning maps alongside the city proposal."""
    from matplotlib.collections import LineCollection, PatchCollection
    from matplotlib.patches import Patch, Polygon
    from matplotlib.lines import Line2D

    if sha256(CITY_CONTEXT.read_bytes()).hexdigest() != CITY_CONTEXT_SHA256:
        raise ValueError("Baghdad city background has changed; review its source before rendering")
    with gzip.open(CITY_CONTEXT, "rt") as source:
        context = json.load(source)

    def rings(geometry):
        kind, coordinates = geometry["type"], geometry["coordinates"]
        if kind == "Polygon":
            return [coordinates[0]]
        if kind == "MultiPolygon":
            return [polygon[0] for polygon in coordinates]
        return []

    def line_parts(geometry):
        kind, coordinates = geometry["type"], geometry["coordinates"]
        if kind == "LineString":
            return [coordinates]
        if kind == "MultiLineString":
            return coordinates
        return []

    def draw_background(ax, bounds):
        ax.set_facecolor("#f0eee4")
        land_colours = {"residential": "#e9e5dc", "commercial": "#e4daca",
                        "industrial": "#ded9d2", "park": "#d7e8d1",
                        "grass": "#dfe9d4", "grassland": "#dfe9d4",
                        "farmland": "#e5ead9", "school": "#e2e8d6",
                        "university": "#dce7d5"}
        patches, colours = [], []
        for feature in context["layers"].get("landuse", []):
            colour = land_colours.get(feature.get("properties", {}).get("kind"))
            if colour is None:
                continue
            for ring in rings(feature["geometry"]):
                if len(ring) >= 3:
                    patches.append(Polygon(ring, closed=True))
                    colours.append(colour)
        if patches:
            ax.add_collection(PatchCollection(patches, facecolors=colours, edgecolors="none", zorder=0.1))
        water_patches, water_lines = [], []
        for feature in context["layers"].get("water", []):
            water_patches.extend(Polygon(ring, closed=True) for ring in rings(feature["geometry"]) if len(ring) >= 3)
            water_lines.extend(line_parts(feature["geometry"]))
        if water_patches:
            ax.add_collection(PatchCollection(water_patches, facecolor="#a9d3e1", edgecolor="none", zorder=.3))
        if water_lines:
            ax.add_collection(LineCollection(water_lines, colors="#9ecddd", linewidths=.8, zorder=.31))
        for kind, colour, width in (("major_road", "#c8bdad", .65),
                                    ("highway", "#c6ac91", 1.0),
                                    ("rail", "#b4a89c", .55)):
            lines = [line for feature in context["layers"].get("roads", [])
                     if feature.get("properties", {}).get("kind") == kind
                     for line in line_parts(feature["geometry"])]
            if lines:
                ax.add_collection(LineCollection(lines, colors=colour, linewidths=width, alpha=.7, zorder=.5))
        west, south, east, north = bounds
        for feature in context["layers"].get("places", []):
            props = feature.get("properties", {})
            if props.get("kind_detail") not in ("city", "town"):
                continue
            x, y = feature["geometry"]["coordinates"]
            label = props.get("name:en")
            if label and west < x < east and south < y < north:
                ax.text(x, y, label, fontsize=6.2, color="#6a716d", alpha=.8,
                        ha="center", va="center", zorder=1)

    styles = {"line": ("#146c85", 1.7), "physical_connector": ("#b77827", 1.6),
              "schematic_control_polyline": ("#238c63", 1.5),
              "straight_lower_bound_connector": ("#b04d54", 1.25)}
    rfi_colours = {"Green": "#21875a", "Red": "#c64c52", "Blue": "#357db7",
                   "Purple": "#8d62ad", "Yellow": "#c6971d", "White": "#66747e",
                   "Airport": "#db713c"}
    for filename, title, destination in zip(
        ("network-148km.geojson", "network-606km.geojson"),
        ("148.2 km | first programme", "605.652 km | metropolitan network"),
        MAP_IMAGES,
    ):
        data = json.loads((HERE / "maps" / filename).read_text())
        fig, ax = plt.subplots(figsize=(8.5, 9), dpi=190)
        fig.patch.set_facecolor("white")
        route_points = [point for feature in data["features"]
                        if feature.get("geometry", {}).get("type") == "LineString"
                        for point in feature["geometry"]["coordinates"]]
        min_x, max_x = min(p[0] for p in route_points), max(p[0] for p in route_points)
        min_y, max_y = min(p[1] for p in route_points), max(p[1] for p in route_points)
        pad_x, pad_y = (max_x - min_x) * .07, (max_y - min_y) * .07
        bounds = (min_x - pad_x, min_y - pad_y, max_x + pad_x, max_y + pad_y)
        draw_background(ax, bounds)
        for feature in data["features"]:
            geometry = feature.get("geometry") or {}
            if geometry.get("type") != "Polygon":
                continue
            if feature.get("properties", {}).get("kind") != "priority_proximity_area":
                continue
            ring = geometry["coordinates"][0]
            ax.fill([p[0] for p in ring], [p[1] for p in ring],
                    color="#f1cf76", alpha=.22, zorder=1)
        for feature in data["features"]:
            geometry = feature.get("geometry") or {}
            if geometry.get("type") != "LineString":
                continue
            kind = feature.get("properties", {}).get("kind")
            colour, width = styles.get(kind, ("#89949d", 0.8))
            if filename == "network-148km.geojson":
                colour = rfi_colours.get(feature.get("properties", {}).get("line"), colour)
                width = 2.25
            points = geometry["coordinates"]
            ax.plot([p[0] for p in points], [p[1] for p in points],
                    color=colour, linewidth=width, alpha=.88, zorder=3)
        for feature in data["features"]:
            geometry = feature.get("geometry") or {}
            if geometry.get("type") != "Point":
                continue
            props = feature.get("properties", {})
            x, y = geometry["coordinates"]
            kind = props.get("kind", "")
            if kind in ("station", "proposed_stop_anchor"):
                ax.scatter(x, y, s=6, color="#384d5a", alpha=.5, zorder=4)
            elif kind in ("proposed_anchor", "proposed_population_anchor"):
                ax.scatter(x, y, s=45, marker="D", color="#bf7324", edgecolor="white", linewidth=.6, zorder=6)
                label = props.get("map_label") or props.get("name") or props.get("rfi_name")
                if label:
                    ax.annotate(label, (x, y), xytext=(5, 5), textcoords="offset points",
                                fontsize=7, color="#663f18", weight="bold", zorder=7)
            elif kind == "rfi_named":
                ax.scatter(x, y, s=9, color="#213b4d", alpha=.75, zorder=5)
                label = props.get("map_label") or ""
                if any(term in label.lower() for term in ("airport", "sadr", "jadri", "chadri")):
                    ax.annotate(label, (x, y), xytext=(5, 4), textcoords="offset points",
                                fontsize=7, color="#17364a", zorder=7)
        ax.set_title(title, fontsize=15, color="#17364a", pad=15, weight="bold")
        ax.set_xlabel("Longitude (°E)", fontsize=8, color="#51616b")
        ax.set_ylabel("Latitude (°N)", fontsize=8, color="#51616b")
        ax.tick_params(labelsize=7, colors="#617781")
        ax.grid(color="#dce5e9", linewidth=.5, zorder=0)
        ax.set_aspect(1 / math.cos(math.radians(33.3)))
        ax.set_xlim(bounds[0], bounds[2])
        ax.set_ylim(bounds[1], bounds[3])
        for spine in ax.spines.values():
            spine.set_color("#c6d2d9")
        if filename == "network-148km.geojson":
            legend = [Line2D([0], [0], color=colour, lw=2.4, label=name) for name, colour in rfi_colours.items()]
        else:
            legend = [Line2D([0], [0], color="#146c85", lw=2, label="Principal route"),
                      Line2D([0], [0], color="#b77827", lw=2, label="Planning connection"),
                      Line2D([0], [0], marker=".", color="#384d5a", lw=0, label="Stop screen")]
        legend.append(Patch(facecolor="#f1cf76", alpha=.4, label="1 km priority access area"))
        ax.legend(handles=legend, loc="lower center", bbox_to_anchor=(.5, -.16), ncol=4,
                  frameon=False, fontsize=8)
        fig.text(.5, .015, "City background: OpenStreetMap, Natural Earth and Protomaps | routes are schematic",
                 ha="center", fontsize=8, color="#51616b")
        fig.tight_layout(rect=(0, .08, 1, .97))
        destination.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(destination, facecolor="white")
        plt.close(fig)


def render():
    map_images()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleOSR", parent=styles["Title"], fontName="Helvetica-Bold",
                              fontSize=18, leading=22, textColor=colors.HexColor("#17364a"), spaceAfter=11))
    styles.add(ParagraphStyle(name="SectionOSR", parent=styles["Heading2"], fontName="Helvetica-Bold",
                              fontSize=11, leading=14, textColor=colors.HexColor("#146c85"), spaceBefore=10, spaceAfter=5))
    styles.add(ParagraphStyle(name="BodyOSR", parent=styles["BodyText"], fontName="Helvetica",
                              fontSize=8.6, leading=12.2, spaceAfter=6))
    styles.add(ParagraphStyle(name="CellOSR", parent=styles["BodyOSR"], fontSize=7.6, leading=10.2, spaceAfter=0))
    styles.add(ParagraphStyle(name="FooterOSR", parent=styles["BodyOSR"], fontSize=7,
                              textColor=colors.HexColor("#697a83"), alignment=TA_CENTER))
    ast = mistune.create_markdown(renderer="ast", plugins=["table"])((HERE / "PROPOSAL.md").read_text())
    story = []
    for node in ast:
        kind = node["type"]
        if kind == "heading":
            style = "TitleOSR" if node["attrs"]["level"] == 1 else "SectionOSR"
            if inline(node["children"]) == "The city and the routes":
                for destination, caption in zip(MAP_IMAGES, (
                    "First programme: seven corridors and priority access areas",
                    "Metropolitan network: principal lines, planning connections and stop screens",
                )):
                    story.append(PageBreak())
                    story.append(Paragraph(caption, styles["SectionOSR"]))
                    story.append(Image(str(destination), width=175 * mm, height=185 * mm))
                    story.append(Paragraph("Lines and points are planning guides; 64 and 280 stations are budget allowances, not approved sites.", styles["FooterOSR"]))
                story.append(PageBreak())
            story.append(Paragraph(inline(node["children"]), styles[style]))
        elif kind == "paragraph":
            story.append(Paragraph(inline(node["children"]), styles["BodyOSR"]))
        elif kind == "table":
            head = node["children"][0]["children"]
            body = node["children"][1]["children"]
            rows = [head] + [row["children"] for row in body]
            cells = [[Paragraph(inline(cell["children"]), styles["CellOSR"]) for cell in row] for row in rows]
            widths = ([35, 18, 16, 18, 30, 30, 16] if len(head) == 7
                      else [38, 25, 24, 40, 43] if len(head) == 5
                      else [28, 47, 47, 48] if len(head) == 4
                      else [34, 66, 70] if len(head) == 3 else None)
            if widths:
                widths = [width * mm for width in widths]
            table = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#deebef")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8f9")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOX", (0, 0), (-1, -1), .4, colors.HexColor("#afc2cb")),
                ("INNERGRID", (0, 0), (-1, -1), .2, colors.HexColor("#d7e1e5")),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.extend((table, Spacer(1, 3 * mm)))
        elif kind == "list":
            for item in node["children"]:
                contents = item.get("children", [])
                text = "".join(inline(child.get("children", [])) for child in contents)
                story.append(Paragraph("• " + text, styles["BodyOSR"]))
    result = json.loads((HERE / "system-results.json").read_text())
    first = result["networks"]["first"]
    metro = result["networks"]["metropolitan"]
    labels = {
        "elevated_civil": "Elevated viaduct and foundations",
        "stations_access": "Accessible stations",
        "track_walkways": "Track and walkways",
        "signalling_comms": "Signalling and communications",
        "brake_protection_recovery": "Braking, protection and recovery",
        "line_traction_supply": "Protected conductor and sections",
        "grid_charging_buffers": "Grid supply",
        "vehicles": "Vehicle fleet",
        "depots_control": "Depots and control",
        "land_utilities_disruption": "Land, utilities and disruption",
        "tooling_recovery": "Tooling and local production",
        "design_assurance": "Design and assurance",
        "testing_commissioning": "Testing and commissioning",
        "project_allowance": "Project allowance",
    }
    story.append(Paragraph("Installed capital by scope", styles["SectionOSR"]))
    rows = [["US$ million", "148.2 km", "605.652 km"]]
    for key, label in labels.items():
        rows.append([label, f"{first['selected_capital_scope_usd_m'][key]:,.3f}",
                     f"{metro['selected_capital_scope_usd_m'][key]:,.3f}"])
    rows.append(["Installed total",
                 f"{first['power_cases'][first['digital_cost_leader']]['installed_capital_usd_m']:,.3f}",
                 f"{metro['power_cases'][metro['digital_cost_leader']]['installed_capital_usd_m']:,.3f}"])
    table = Table([[Paragraph(html.escape(value), styles["CellOSR"]) for value in row]
                   for row in rows], colWidths=[94 * mm, 38 * mm, 38 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#deebef")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#deebef")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f5f8f9")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOX", (0, 0), (-1, -1), .4, colors.HexColor("#afc2cb")),
    ]))
    story.append(table)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=16 * mm,
                            leftMargin=16 * mm, topMargin=15 * mm, bottomMargin=17 * mm,
                            title="OpenSourceRail Baghdad metropolitan railway", author="OpenSourceRail")
    def footer(canvas, document):
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#697a83"))
        canvas.drawString(16 * mm, 10 * mm, "OpenSourceRail | Amanat Baghdad planning proposal | 18 November 2026")
        canvas.drawRightString(194 * mm, 10 * mm, str(document.page))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    render()
