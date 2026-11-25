"""Render the Baghdad proposal from its Markdown source and published maps."""

from __future__ import annotations

import html
import json
from urllib.parse import urljoin
from io import BytesIO
from pathlib import Path

import cairosvg
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mistune
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "Baghdad-Metro-Proposal.pdf"


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
            url = urljoin("https://github.com/modernecotech/OpenSourceRail/blob/main/cities/Baghdad/PROPOSAL.md",
                          node["attrs"]["url"])
            out.append(f'<link href="{html.escape(url, quote=True)}">{inline(node["children"])}</link>')
        elif "children" in node:
            out.append(inline(node["children"]))
    return "".join(out)


class ProposalFigure(Flowable):
    """Keep the illustration and its credit together at a readable printed size."""

    def __init__(self, path, caption):
        super().__init__()
        source = (BytesIO(cairosvg.svg2png(url=str(path), output_width=1800))
                  if path.suffix == ".svg" else str(path))
        self.picture = Image(source, width=174 * mm, height=164 * mm, kind="proportional")
        self.width_at_full_size = self.picture.drawWidth
        self.height_at_full_size = self.picture.drawHeight
        self.caption = caption
        self.spaceBefore = self.spaceAfter = 2 * mm

    def wrap(self, width, height):
        _, self.caption_height = self.caption.wrap(width, height)
        available = height - self.caption_height - 2 * mm
        # Modest resizing can keep a figure with its discussion. A larger
        # reduction makes screenshot text hard to read, so move it to the next page.
        scale = min(width / self.width_at_full_size, 1, max(.82, available / self.height_at_full_size))
        self.picture.drawWidth = self.width_at_full_size * scale
        self.picture.drawHeight = self.height_at_full_size * scale
        self.width = width
        self.height = self.picture.drawHeight + self.caption_height + 2 * mm
        return self.width, self.height

    def draw(self):
        self.caption.drawOn(self.canv, 0, 0)
        self.picture.drawOn(self.canv, (self.width - self.picture.drawWidth) / 2,
                            self.caption_height + 2 * mm)


def render():
    result = json.loads((HERE / "system-results.json").read_text())
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleOSR", parent=styles["Title"], fontName="Helvetica-Bold",
                              fontSize=18, leading=22, textColor=colors.HexColor("#17364a"), spaceAfter=11))
    styles.add(ParagraphStyle(name="SectionOSR", parent=styles["Heading2"], fontName="Helvetica-Bold",
                              fontSize=11, leading=14, textColor=colors.HexColor("#146c85"), spaceBefore=10, spaceAfter=5,
                              keepWithNext=True))
    styles.add(ParagraphStyle(name="SubsectionOSR", parent=styles["SectionOSR"],
                              fontSize=10, leading=13, spaceBefore=7))
    styles.add(ParagraphStyle(name="BodyOSR", parent=styles["BodyText"], fontName="Helvetica",
                              fontSize=8.6, leading=12.0, spaceAfter=5.5))
    styles.add(ParagraphStyle(name="CellOSR", parent=styles["BodyOSR"], fontSize=7.6, leading=10.2, spaceAfter=0))
    styles.add(ParagraphStyle(name="FooterOSR", parent=styles["BodyOSR"], fontSize=7,
                              textColor=colors.HexColor("#697a83"), alignment=TA_CENTER))
    proposal = (HERE / "PROPOSAL.md").read_text()
    proposal_date = next(line for line in proposal.splitlines() if line.startswith("**Proposal to Amanat Baghdad · ")).split(" · ")[1]
    ast = mistune.create_markdown(renderer="ast", plugins=["table"])(proposal)
    story = []
    current_section = ""
    def figure(node, caption):
        path = (HERE / node["attrs"]["url"]).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError(f"Missing local proposal figure {path.name}")
        return ProposalFigure(path, Paragraph(caption, styles["FooterOSR"]))

    def cash_chart():
        cash = {name: result["networks"][name]["selected_construction_cashflow"]
                for name in ("first", "metropolitan")}
        years = list(range(min(row["year"] for value in cash.values() for row in value["annual_capital_draw"]),
                           max(row["year"] for value in cash.values() for row in value["annual_capital_draw"]) + 1))
        amounts = {name: {row["year"]: row["capital_usd_m"] for row in value["annual_capital_draw"]}
                   for name, value in cash.items()}
        first = [amounts["first"].get(year, 0.0) for year in years]
        metro = [amounts["metropolitan"].get(year, 0.0) for year in years]
        for values, name in ((first, "first"), (metro, "metropolitan")):
            capital = cash[name]["total_capital_usd_m"]
            if abs(sum(values) - capital) > .01:
                raise ValueError(f"Construction cash chart does not reconcile with {name} capital")
        fig, ax = plt.subplots(figsize=(9, 3.4), dpi=170)
        fig.patch.set_facecolor("white")
        x = list(range(len(years)))
        ax.bar([v - .18 for v in x], [v / 1000 for v in first], width=.35, color="#b77827", label="Seven corridors")
        ax.bar([v + .18 for v in x], [v / 1000 for v in metro], width=.35, color="#146c85", label="Independent citywide")
        ax.set_xticks(x, years)
        ax.set_ylabel("US$ billion, 2026 prices")
        ax.set_title("Annual construction capital draw", loc="left", color="#17364a", weight="bold")
        ax.grid(axis="y", color="#dae4e8", linewidth=.7)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(frameon=False, ncol=2, loc="upper left")
        fig.tight_layout()
        png = BytesIO()
        fig.savefig(png, format="png", facecolor="white")
        plt.close(fig)
        png.seek(0)
        return Image(png, width=174 * mm, height=66 * mm)
    blocks = iter(node for node in ast if node["type"] != "blank_line")
    for node in blocks:
        kind = node["type"]
        if kind == "heading":
            level = node["attrs"]["level"]
            if level == 2:
                current_section = inline(node["children"])
            style = {1: "TitleOSR", 2: "SectionOSR"}.get(level, "SubsectionOSR")
            story.append(Paragraph(inline(node["children"]), styles[style]))
        elif kind == "paragraph":
            children = node["children"]
            if len(children) == 1 and children[0]["type"] == "image":
                caption = next(blocks, {})
                if (caption.get("type") != "paragraph" or len(caption["children"]) != 1
                        or caption["children"][0]["type"] != "emphasis"):
                    raise ValueError(f"Add a caption below {children[0]['attrs']['url']}")
                story.append(figure(children[0], inline(caption["children"])))
                continue
            content = inline(node["children"])
            paragraph = Paragraph(content, styles["BodyOSR"])
            story.append(KeepTogether([paragraph]) if content.startswith((
                "At a <b>1.5 kV calculation setting</b>",
                "Annual train-km use the declared hourly departure pattern",
                "The seven-corridor illustrative loan",
            ))
                         else paragraph)
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
            if current_section == "Capital, construction cash and delivery":
                story.append(cash_chart())
        elif kind == "list":
            for item in node["children"]:
                contents = item.get("children", [])
                text = "".join(inline(child.get("children", [])) for child in contents)
                story.append(Paragraph("• " + text, styles["BodyOSR"]))
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
    story.append(PageBreak())
    story.append(Paragraph("Appendix · Common bid-control prices by scope", styles["SectionOSR"]))
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
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph("How to use this estimate", styles["SectionOSR"]))
    story.append(Paragraph("Each row is an installed 2026 US-dollar planning allowance for its own network. The project allowance is 20% of the preceding subtotal. Control electronics are allocated within vehicles, stations, signalling, grid and control rooms. The annual operating and 30-year present-cost figures elsewhere in the proposal are additional lifecycle measures and should not be added to installed capital.", styles["BodyOSR"]))
    story.append(Paragraph("The two network totals are independent choices. The seven-corridor capital cannot be treated as a first-stage payment toward the citywide network. No revenue, interest during construction, export-credit premium, tax or foreign-exchange adjustment is included. GIS linework and station counts are planning controls until corridor and station schedules are settled.", styles["BodyOSR"]))
    story.append(Paragraph("For quotation, issue the controlled train, span, station, power and control interfaces with a bill of quantities, supplier origin, local work content, annual delivery capacity and renewal prices. The sponsoring authority can then update the same calculation with firm prices and financing terms.", styles["BodyOSR"]))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    class ProposalDocument(SimpleDocTemplate):
        def afterFlowable(self, flowable):
            if isinstance(flowable, Paragraph) and flowable.style.name in ("SectionOSR", "SubsectionOSR"):
                title = flowable.getPlainText()
                bookmark = self.seq.nextf("proposal-heading")
                self.canv.bookmarkPage(bookmark)
                self.canv.addOutlineEntry(title, bookmark, level=int(flowable.style.name == "SubsectionOSR"))

    doc = ProposalDocument(str(OUTPUT), pagesize=A4, rightMargin=16 * mm,
                            leftMargin=16 * mm, topMargin=15 * mm, bottomMargin=17 * mm,
                            title="OpenSourceRail Baghdad metropolitan railway", author="OpenSourceRail")
    def footer(canvas, document):
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#697a83"))
        canvas.drawString(16 * mm, 10 * mm, f"OpenSourceRail | Amanat Baghdad planning proposal | {proposal_date}")
        canvas.drawRightString(194 * mm, 10 * mm, str(document.page))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    render()
