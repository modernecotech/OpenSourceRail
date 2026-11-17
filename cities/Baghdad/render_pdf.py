"""Render the Baghdad proposal from its single Markdown source and two GIS maps."""

from __future__ import annotations

import html
import json
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
OUTPUT = ROOT / "output/pdf/Baghdad-Metro-v0.7-Proposal.pdf"
TMP = ROOT / "tmp/pdfs/baghdad-v07-network.png"
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


def map_image():
    TMP.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), dpi=180)
    styles = {"line": ("#146c85", 1.0), "physical_connector": ("#b77827", 1.15),
              "schematic_control_polyline": ("#238c63", 1.3),
              "straight_lower_bound_connector": ("#b04d54", 1.0)}
    rfi_colours = {"Green": "#21875a", "Red": "#c64c52", "Blue": "#357db7",
                   "Purple": "#8d62ad", "Yellow": "#c6971d", "White": "#66747e",
                   "Airport": "#db713c"}
    for ax, filename, title in zip(axes,
            ("network-148km.geojson", "network-606km.geojson"),
            ("148.2 km first programme", "605.65 km metropolitan screen")):
        data = json.loads((HERE / "maps" / filename).read_text())
        for feature in data["features"]:
            geometry = feature.get("geometry") or {}
            if geometry.get("type") != "LineString":
                continue
            kind = feature.get("properties", {}).get("kind")
            colour, width = styles.get(kind, ("#89949d", 0.8))
            if filename == "network-148km.geojson":
                colour = rfi_colours.get(feature.get("properties", {}).get("line"), colour)
                width = 1.25
            points = geometry["coordinates"]
            ax.plot([p[0] for p in points], [p[1] for p in points],
                    color=colour, linewidth=width, alpha=0.85)
        ax.set_title(title, fontsize=10, color="#17364a", pad=8)
        ax.set_aspect("equal", adjustable="datalim")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color("#c6d2d9")
    fig.text(.5, .015, "Schematic links and access points; no surveyed alignment or station site",
             ha="center", fontsize=8, color="#51616b")
    fig.tight_layout(rect=(0, .04, 1, 1), w_pad=2.0)
    fig.savefig(TMP, facecolor="white")
    plt.close(fig)


def render():
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
            if inline(node["children"]) == "Service and railway":
                story.append(PageBreak())
            story.append(Paragraph(inline(node["children"]), styles[style]))
            if style == "TitleOSR":
                map_image()
                story.append(Image(str(TMP), width=178 * mm, height=67 * mm))
                story.append(Spacer(1, 3 * mm))
        elif kind == "paragraph":
            story.append(Paragraph(inline(node["children"]), styles["BodyOSR"]))
        elif kind == "table":
            head = node["children"][0]["children"]
            body = node["children"][1]["children"]
            rows = [head] + [row["children"] for row in body]
            cells = [[Paragraph(inline(cell["children"]), styles["CellOSR"]) for cell in row] for row in rows]
            widths = [34 * mm, 72 * mm, 72 * mm] if len(head) == 3 else None
            table = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#deebef")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8f9")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOX", (0, 0), (-1, -1), .4, colors.HexColor("#afc2cb")),
                ("INNERGRID", (0, 0), (-1, -1), .2, colors.HexColor("#d7e1e5")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.extend((table, Spacer(1, 3 * mm)))
        elif kind == "list":
            for item in node["children"]:
                contents = item.get("children", [])
                text = "".join(inline(child.get("children", [])) for child in contents)
                story.append(Paragraph("• " + text, styles["BodyOSR"]))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=16 * mm,
                            leftMargin=16 * mm, topMargin=15 * mm, bottomMargin=17 * mm,
                            title="OpenSourceRail Baghdad urban rail proposal", author="OpenSourceRail")
    def footer(canvas, document):
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#697a83"))
        canvas.drawString(16 * mm, 10 * mm, "OpenSourceRail | Amanat Baghdad engineering concept | 17 November 2026")
        canvas.drawRightString(194 * mm, 10 * mm, str(document.page))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    TMP.unlink(missing_ok=True)
    print(OUTPUT)


if __name__ == "__main__":
    render()
