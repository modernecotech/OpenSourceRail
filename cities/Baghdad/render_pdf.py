"""Render the Baghdad proposal from its Markdown source and published maps."""

from __future__ import annotations

import html
import json
from hashlib import sha256
from urllib.parse import urljoin
from io import BytesIO
from pathlib import Path

import cairosvg
import mistune
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


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
    record = HERE / "straight-through-network.json"
    source = HERE / "PROPOSAL.md"
    inputs = {record, source, Path(__file__).resolve()}
    cost = json.loads(record.read_text())["cost"]["cost_cases"]
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
    proposal = source.read_text()
    proposal_date = next(line for line in proposal.splitlines() if line.startswith("**Proposal to Amanat Baghdad · ")).split(" · ")[1]
    ast = mistune.create_markdown(renderer="ast", plugins=["table"])(proposal)
    story = []
    def figure(node, caption):
        path = (HERE / node["attrs"]["url"]).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError(f"Missing local proposal figure {path.name}")
        inputs.add(path)
        return ProposalFigure(path, Paragraph(caption, styles["FooterOSR"]))

    blocks = iter(node for node in ast if node["type"] != "blank_line")
    for node in blocks:
        kind = node["type"]
        if kind == "heading":
            level = node["attrs"]["level"]
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
    story.append(PageBreak())
    story.append(Paragraph("Appendix · Metropolitan planning allowances by scope", styles["SectionOSR"]))
    cases = ("low", "base", "high")
    rows = [["US$ million", "Low", "Base", "High"]]
    for key in cost["base"]["direct_scope_usd_m"]:
        rows.append([key.replace("_", " ").capitalize(),
                     *(f"{cost[case]['direct_scope_usd_m'][key]:,.3f}" for case in cases)])
    for key, label in (("design_usd_m", "Design"), ("testing_usd_m", "Testing and commissioning"),
                       ("allowance_usd_m", "Project allowance"), ("installed_planning_usd_m", "Installed planning allowance")):
        rows.append([label, *(f"{cost[case][key]:,.3f}" for case in cases)])
    table = Table([[Paragraph(html.escape(value), styles["CellOSR"]) for value in row]
                   for row in rows], colWidths=[76 * mm, 33 * mm, 33 * mm, 33 * mm], repeatRows=1)
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
    story.append(Paragraph("The allowances use constant 2026 US dollars. River crossings and other held works need "
                           "project designs and prices. Construction draws and funding terms require a verified delivery schedule.",
                           styles["BodyOSR"]))
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
                            title="OpenSourceRail Baghdad metropolitan railway", author="OpenSourceRail", invariant=True)
    def footer(canvas, document):
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#697a83"))
        canvas.drawString(16 * mm, 10 * mm, f"OpenSourceRail | Amanat Baghdad planning proposal | {proposal_date}")
        canvas.drawRightString(194 * mm, 10 * mm, str(document.page))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    receipt = {
        "artifact": OUTPUT.relative_to(ROOT).as_posix(),
        "sha256": sha256(OUTPUT.read_bytes()).hexdigest(),
        "source_sha256": {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest()
                          for path in sorted(inputs)},
    }
    (HERE / "proposal-pdf.receipt.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    render()
