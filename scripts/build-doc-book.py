#!/usr/bin/env python3
"""Build a single PDF book from the OpenSourceRail documentation.

The book includes:

1. The repository root README.
2. The generated design catalogue index.
3. Every Markdown file under docs/.
4. Every generated city README under designs/<region>/<country>/<city>/.

The renderer is intentionally self-contained. The repo image set is large,
so local images are downsampled into build/doc-book-assets before being
embedded in the PDF.
"""

from __future__ import annotations

import argparse
import html
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import mistune
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO_ROOT / "build" / "opensource-rail-docs-book.pdf"
ASSET_CACHE = REPO_ROOT / "build" / "doc-book-assets"


@dataclass(frozen=True)
class SourceDoc:
    path: Path
    title: str
    part: str


def _register_fonts() -> None:
    font_root = Path("/usr/share/fonts/truetype")
    candidates = {
        "BookSans": font_root / "Roboto-Regular.ttf",
        "BookSans-Bold": font_root / "Roboto-Bold.ttf",
        "BookSans-Italic": font_root / "Roboto-Italic.ttf",
        "BookMono": font_root / "DejaVuSansMono.ttf",
    }
    for name, path in candidates.items():
        if path.exists():
            pdfmetrics.registerFont(TTFont(name, str(path)))


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    styles: dict[str, ParagraphStyle] = {}
    font = "BookSans" if "BookSans" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
    bold = "BookSans-Bold" if "BookSans-Bold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"
    italic = "BookSans-Italic" if "BookSans-Italic" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Oblique"
    mono = "BookMono" if "BookMono" in pdfmetrics.getRegisteredFontNames() else "Courier"

    styles["title"] = ParagraphStyle(
        "BookTitle",
        parent=base["Title"],
        fontName=bold,
        fontSize=26,
        leading=32,
        alignment=TA_CENTER,
        spaceAfter=18,
    )
    styles["subtitle"] = ParagraphStyle(
        "BookSubtitle",
        parent=base["Normal"],
        fontName=font,
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#475569"),
        spaceAfter=10,
    )
    styles["part"] = ParagraphStyle(
        "Part",
        parent=base["Heading1"],
        fontName=bold,
        fontSize=22,
        leading=28,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=14,
    )
    for level, size in [(1, 18), (2, 15), (3, 13), (4, 11), (5, 10), (6, 10)]:
        styles[f"h{level}"] = ParagraphStyle(
            f"Heading{level}",
            parent=base["Heading1"],
            fontName=bold,
            fontSize=size,
            leading=size + 4,
            textColor=colors.HexColor("#111827"),
            spaceBefore=10 if level <= 2 else 7,
            spaceAfter=5,
        )
    styles["body"] = ParagraphStyle(
        "Body",
        parent=base["BodyText"],
        fontName=font,
        fontSize=9,
        leading=12,
        spaceAfter=5,
    )
    styles["small"] = ParagraphStyle(
        "Small",
        parent=styles["body"],
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#334155"),
    )
    styles["caption"] = ParagraphStyle(
        "Caption",
        parent=styles["small"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#475569"),
        spaceBefore=2,
        spaceAfter=7,
    )
    styles["code"] = ParagraphStyle(
        "Code",
        parent=base["Code"],
        fontName=mono,
        fontSize=6.5,
        leading=8,
        leftIndent=8,
        rightIndent=4,
        backColor=colors.HexColor("#f8fafc"),
        borderColor=colors.HexColor("#e2e8f0"),
        borderWidth=0.4,
        borderPadding=4,
        spaceBefore=4,
        spaceAfter=6,
    )
    styles["list"] = ParagraphStyle(
        "List",
        parent=styles["body"],
        leftIndent=8,
        bulletIndent=0,
    )
    styles["table"] = ParagraphStyle(
        "TableCell",
        parent=styles["small"],
        fontSize=6.2,
        leading=7.5,
        wordWrap="CJK",
    )
    styles["table_head"] = ParagraphStyle(
        "TableHead",
        parent=styles["table"],
        fontName=bold,
        textColor=colors.white,
    )
    styles["em"] = ParagraphStyle("Italic", parent=styles["body"], fontName=italic)
    return styles


def _doc_sources() -> list[SourceDoc]:
    docs: list[SourceDoc] = [
        SourceDoc(REPO_ROOT / "README.md", "Repository README", "Front Matter"),
        SourceDoc(REPO_ROOT / "designs" / "INDEX.md", "Design Catalogue Index", "Design Catalogue"),
    ]
    docs.extend(
        SourceDoc(path, path.relative_to(REPO_ROOT).as_posix(), "Docs")
        for path in sorted((REPO_ROOT / "docs").rglob("*.md"))
    )
    city_readmes = sorted((REPO_ROOT / "designs").glob("*/*/*/README.md"))
    docs.extend(
        SourceDoc(
            path,
            path.parent.relative_to(REPO_ROOT / "designs").as_posix(),
            "Generated City Designs",
        )
        for path in city_readmes
    )
    return docs


def _plain_inline(children: list[dict] | None) -> str:
    if not children:
        return ""
    parts: list[str] = []
    for child in children:
        t = child.get("type")
        if t in {"text", "codespan"}:
            parts.append(child.get("raw", ""))
        elif t in {"strong", "emphasis", "link", "image"}:
            parts.append(_plain_inline(child.get("children")))
        elif t in {"softbreak", "linebreak"}:
            parts.append(" ")
    return "".join(parts)


def _inline(children: list[dict] | None) -> str:
    if not children:
        return ""
    parts: list[str] = []
    for child in children:
        t = child.get("type")
        if t == "text":
            parts.append(html.escape(child.get("raw", "")))
        elif t == "softbreak":
            parts.append(" ")
        elif t == "linebreak":
            parts.append("<br/>")
        elif t == "codespan":
            parts.append(f"<font name=\"BookMono\">{html.escape(child.get('raw', ''))}</font>")
        elif t == "strong":
            parts.append(f"<b>{_inline(child.get('children'))}</b>")
        elif t == "emphasis":
            parts.append(f"<i>{_inline(child.get('children'))}</i>")
        elif t == "link":
            label = _inline(child.get("children")) or html.escape(child.get("attrs", {}).get("url", ""))
            parts.append(f"<font color=\"#2563eb\">{label}</font>")
        elif t == "image":
            alt = _plain_inline(child.get("children")) or child.get("attrs", {}).get("url", "")
            parts.append(html.escape(alt))
        elif "children" in child:
            parts.append(_inline(child.get("children")))
    return "".join(parts)


def _paragraph_from_inline(children: list[dict] | None, styles: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(_inline(children), styles["body"])


def _resolve_link(url: str, base_path: Path) -> Path | None:
    if not url or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", url):
        return None
    clean = url.split("#", 1)[0]
    if not clean:
        return None
    path = (base_path.parent / clean).resolve()
    try:
        path.relative_to(REPO_ROOT)
    except ValueError:
        return None
    return path if path.exists() else None


def _cached_image(path: Path, max_px: int, quality: int) -> Path | None:
    try:
        stat = path.stat()
        rel = path.relative_to(REPO_ROOT).as_posix().replace("/", "__")
        out = ASSET_CACHE / f"{rel}.{max_px}.{quality}.jpg"
        if out.exists() and out.stat().st_mtime >= stat.st_mtime:
            return out
        ASSET_CACHE.mkdir(parents=True, exist_ok=True)
        with PILImage.open(path) as im:
            im = im.convert("RGB")
            im.thumbnail((max_px, max_px), PILImage.Resampling.LANCZOS)
            im.save(out, "JPEG", quality=quality, optimize=True)
        return out
    except Exception:
        return None


def _image_flowables(
    token: dict,
    base_path: Path,
    styles: dict[str, ParagraphStyle],
    max_width: float,
    max_height: float,
    max_px: int,
    quality: int,
) -> list:
    url = token.get("attrs", {}).get("url", "")
    path = _resolve_link(url, base_path)
    if not path:
        return [Paragraph(f"[missing image: {html.escape(url)}]", styles["caption"])]
    cached = _cached_image(path, max_px=max_px, quality=quality)
    if not cached:
        return [Paragraph(f"[unreadable image: {html.escape(path.name)}]", styles["caption"])]
    try:
        with PILImage.open(cached) as im:
            width, height = im.size
        scale = min(max_width / width, max_height / height, 1.0)
        flowables = [Image(str(cached), width=width * scale, height=height * scale)]
        caption = _plain_inline(token.get("children"))
        if caption:
            flowables.append(Paragraph(html.escape(caption), styles["caption"]))
        return flowables
    except Exception:
        return [Paragraph(f"[image failed: {html.escape(path.name)}]", styles["caption"])]


def _table_flowable(token: dict, styles: dict[str, ParagraphStyle], page_width: float):
    rows: list[list[Paragraph]] = []
    for child in token.get("children", []):
        if child.get("type") == "table_head":
            rows.append(
                [
                    Paragraph(_inline(cell.get("children")), styles["table_head"])
                    for cell in child.get("children", [])
                ]
            )
        elif child.get("type") == "table_body":
            for row in child.get("children", []):
                rows.append(
                    [
                        Paragraph(_inline(cell.get("children")), styles["table"])
                        for cell in row.get("children", [])
                    ]
                )
    if not rows:
        return Spacer(1, 0)
    cols = max(len(row) for row in rows)
    for row in rows:
        while len(row) < cols:
            row.append(Paragraph("", styles["table"]))
    col_width = page_width / cols
    table = Table(rows, colWidths=[col_width] * cols, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return table


def _render_list(token: dict, styles: dict[str, ParagraphStyle]) -> ListFlowable:
    ordered = token.get("attrs", {}).get("ordered", False)
    items = []
    for item in token.get("children", []):
        parts = []
        for child in item.get("children", []):
            if child.get("type") == "block_text":
                parts.append(Paragraph(_inline(child.get("children")), styles["list"]))
            elif child.get("type") == "paragraph":
                parts.append(_paragraph_from_inline(child.get("children"), styles))
            elif child.get("type") == "list":
                parts.append(_render_list(child, styles))
        if not parts:
            parts.append(Paragraph(_plain_inline(item.get("children")), styles["list"]))
        items.append(ListItem(parts, leftIndent=10))
    return ListFlowable(items, bulletType="1" if ordered else "bullet", leftIndent=14)


def _render_markdown(
    path: Path,
    styles: dict[str, ParagraphStyle],
    page_width: float,
    page_height: float,
    max_image_px: int,
    image_quality: int,
    include_images: bool,
) -> list:
    parser = mistune.create_markdown(renderer="ast", plugins=["table", "strikethrough"])
    text = path.read_text(errors="replace")
    tokens = parser(text)
    flowables: list = []

    for token in tokens:
        t = token.get("type")
        if t == "blank_line":
            continue
        if t == "heading":
            level = min(int(token.get("attrs", {}).get("level", 2)), 6)
            flowables.append(Paragraph(_inline(token.get("children")), styles[f"h{level}"]))
        elif t == "paragraph":
            children = token.get("children", [])
            if include_images and len(children) == 1 and children[0].get("type") == "image":
                flowables.extend(
                    _image_flowables(
                        children[0],
                        path,
                        styles,
                        max_width=page_width,
                        max_height=page_height * 0.45,
                        max_px=max_image_px,
                        quality=image_quality,
                    )
                )
            else:
                flowables.append(_paragraph_from_inline(children, styles))
        elif t == "block_code":
            raw = token.get("raw", "").rstrip()
            if raw:
                flowables.append(Preformatted(raw, styles["code"], maxLineLength=120))
        elif t == "list":
            flowables.append(_render_list(token, styles))
        elif t == "table":
            flowables.append(_table_flowable(token, styles, page_width))
            flowables.append(Spacer(1, 5))
        elif t == "thematic_break":
            flowables.append(Spacer(1, 8))
        elif "raw" in token:
            flowables.append(Paragraph(html.escape(token.get("raw", "")), styles["body"]))
    return flowables


def _page_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("BookSans" if "BookSans" in pdfmetrics.getRegisteredFontNames() else "Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawRightString(A4[0] - 1.5 * cm, 1.0 * cm, f"Page {doc.page}")
    canvas.drawString(1.5 * cm, 1.0 * cm, "OpenSourceRail documentation book")
    canvas.restoreState()


def _part_index(docs: Iterable[SourceDoc]) -> dict[str, list[SourceDoc]]:
    grouped: dict[str, list[SourceDoc]] = {}
    for doc in docs:
        grouped.setdefault(doc.part, []).append(doc)
    return grouped


def build_pdf(out_path: Path, include_images: bool, max_image_px: int, image_quality: int) -> None:
    _register_fonts()
    styles = _styles()
    docs = _doc_sources()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    page_width, page_height = A4
    left = right = 1.45 * cm
    top = bottom = 1.55 * cm
    content_width = page_width - left - right
    content_height = page_height - top - bottom

    story: list = [
        Spacer(1, 5 * cm),
        Paragraph("OpenSourceRail Documentation Book", styles["title"]),
        Paragraph(
            "Root README, docs tree, generated catalogue index, and every region/country/city design README.",
            styles["subtitle"],
        ),
        Paragraph(f"Generated from {len(docs)} Markdown source files.", styles["subtitle"]),
        PageBreak(),
        Paragraph("Included Files", styles["part"]),
    ]
    for part, part_docs in _part_index(docs).items():
        story.append(Paragraph(html.escape(part), styles["h2"]))
        for source in part_docs:
            rel = source.path.relative_to(REPO_ROOT).as_posix()
            story.append(Paragraph(html.escape(rel), styles["small"]))
    story.append(PageBreak())

    current_part: str | None = None
    for idx, source in enumerate(docs):
        if idx > 0:
            story.append(PageBreak())
        if source.part != current_part:
            current_part = source.part
            story.append(Paragraph(html.escape(current_part), styles["part"]))
        rel = source.path.relative_to(REPO_ROOT).as_posix()
        story.append(Paragraph(html.escape(source.title), styles["h1"]))
        story.append(Paragraph(html.escape(rel), styles["small"]))
        story.append(Spacer(1, 6))
        story.extend(
            _render_markdown(
                source.path,
                styles,
                page_width=content_width,
                page_height=content_height,
                max_image_px=max_image_px,
                image_quality=image_quality,
                include_images=include_images,
            )
        )

    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        rightMargin=right,
        leftMargin=left,
        topMargin=top,
        bottomMargin=bottom,
        title="OpenSourceRail Documentation Book",
        author="OpenSourceRail",
    )
    doc.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output PDF path.")
    parser.add_argument("--no-images", action="store_true", help="Skip local images.")
    parser.add_argument("--max-image-px", type=int, default=1400, help="Maximum cached image dimension.")
    parser.add_argument("--image-quality", type=int, default=72, help="JPEG quality for cached images.")
    args = parser.parse_args()

    os.chdir(REPO_ROOT)
    build_pdf(
        out_path=args.out,
        include_images=not args.no_images,
        max_image_px=args.max_image_px,
        image_quality=args.image_quality,
    )
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
