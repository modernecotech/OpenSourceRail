#!/usr/bin/env python3
"""Build the source-bound current maglev reader book."""
from __future__ import annotations

import argparse

import hashlib

import html

import io

import json

import os

import re

import sys




from pathlib import Path

from urllib.parse import quote, unquote

import mistune

from cairosvg import svg2png

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

REPO_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(REPO_ROOT))

DEFAULT_OUT = REPO_ROOT / "OpenSourceRail-Book.pdf"

ASSET_CACHE = REPO_ROOT / "build" / "doc-book-assets"

IMAGE_ERRORS: list[str] = []

REPOSITORY_BLOB_URL = "https://github.com/modernecotech/OpenSourceRail/blob/main"

class BookDocTemplate(SimpleDocTemplate):
    """Add stable PDF outline entries for marked book headings."""

    def afterFlowable(self, flowable) -> None:
        bookmark = getattr(flowable, "book_bookmark", None)
        if bookmark is None:
            return
        title = getattr(flowable, "book_title")
        level = getattr(flowable, "book_level")
        self.canv.bookmarkPage(bookmark)
        self.canv.addOutlineEntry(title, bookmark, level=level, closed=level > 0)

def _outline_heading(text: str, style: ParagraphStyle, key: str, level: int) -> Paragraph:
    heading = Paragraph(html.escape(text), style)
    heading.book_bookmark = key
    heading.book_title = text
    heading.book_level = level
    return heading

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
        keepWithNext=1,
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
            keepWithNext=1,
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
    styles["source"] = ParagraphStyle(
        "Source",
        parent=styles["small"],
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#475569"),
        backColor=colors.HexColor("#f1f5f9"),
        borderColor=colors.HexColor("#cbd5e1"),
        borderWidth=0.4,
        borderPadding=4,
        spaceBefore=1,
        spaceAfter=8,
        keepWithNext=1,
        wordWrap="CJK",
    )
    styles["quote"] = ParagraphStyle(
        "Quote",
        parent=styles["body"],
        textColor=colors.HexColor("#334155"),
        spaceAfter=4,
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

def _filtered_markdown_text(path: Path) -> str:
    text = path.read_text(errors="replace")
    if path == REPO_ROOT / "README.md":
        # The PDF has its own compact contents and city directory. The
        # README's repository tree is useful on GitHub but noisy in book form.
        text = re.sub(
            r"\n## Repository layout\n.*?(?=\n## Quick start\n)",
            "\n",
            text,
            flags=re.S,
        )
    return text

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
        elif t == "inline_html":
            raw = child.get("raw", "")
            parts.append("<br/>" if raw.lower() == "<br>" else html.escape(raw))
        elif t == "codespan":
            parts.append(f"<font name=\"Courier\">{html.escape(child.get('raw', ''))}</font>")
        elif t == "strong":
            parts.append(f"<b>{_inline(child.get('children'))}</b>")
        elif t == "emphasis":
            parts.append(f"<i>{_inline(child.get('children'))}</i>")
        elif t == "strikethrough":
            parts.append(f"<strike>{_inline(child.get('children'))}</strike>")
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
    clean = unquote(url.split("#", 1)[0].split('?', 1)[0])
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
        source = io.BytesIO(svg2png(url=str(path))) if path.suffix.lower() == ".svg" else path
        with PILImage.open(source) as im:
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
        IMAGE_ERRORS.append(f"{base_path.relative_to(REPO_ROOT)}: missing image {url}")
        return [Paragraph(f"[missing image: {html.escape(url)}]", styles["caption"])]
    cached = _cached_image(path, max_px=max_px, quality=quality)
    if not cached:
        IMAGE_ERRORS.append(f"{base_path.relative_to(REPO_ROOT)}: unreadable image {path.name}")
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
        IMAGE_ERRORS.append(f"{base_path.relative_to(REPO_ROOT)}: failed image {path.name}")
        return [Paragraph(f"[image failed: {html.escape(path.name)}]", styles["caption"])]

def _table_flowable(
    token: dict,
    styles: dict[str, ParagraphStyle],
    page_width: float,
    page_height: float,
    base_path: Path,
    include_images: bool,
    max_image_px: int,
    image_quality: int,
):
    raw_rows: list[list[tuple[list[dict], bool]]] = []
    for child in token.get("children", []):
        if child.get("type") == "table_head":
            raw_rows.append(
                [
                    (cell.get("children", []), True)
                    for cell in child.get("children", [])
                ]
            )
        elif child.get("type") == "table_body":
            for row in child.get("children", []):
                raw_rows.append(
                    [
                        (cell.get("children", []), False)
                        for cell in row.get("children", [])
                    ]
                )
    if not raw_rows:
        return Spacer(1, 0)
    cols = max(len(row) for row in raw_rows)
    col_width = page_width / cols
    rows: list[list] = []
    for raw_row in raw_rows:
        rendered_row: list = []
        for children, is_header in raw_row:
            if include_images and len(children) == 1 and children[0].get("type") == "image":
                rendered_row.append(
                    _image_flowables(
                        children[0],
                        base_path,
                        styles,
                        max_width=max(col_width - 8, 1),
                        max_height=page_height * 0.22,
                        max_px=max_image_px,
                        quality=image_quality,
                    )
                )
            else:
                rendered_row.append(
                    Paragraph(_inline(children), styles["table_head" if is_header else "table"])
                )
        rows.append(rendered_row)
    for row in rows:
        while len(row) < cols:
            row.append(Paragraph("", styles["table"]))
    table = Table(rows, colWidths=[col_width] * cols, repeatRows=1, splitInRow=1)
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

def _block_quote_flowable(
    token: dict, styles: dict[str, ParagraphStyle], page_width: float
) -> Table:
    contents: list = []
    for child in token.get("children", []):
        child_type = child.get("type")
        if child_type == "paragraph":
            children = list(child.get("children", []))
            prefix = ""
            if children and children[0].get("type") == "text":
                marker = children[0].get("raw", "")
                labels = {"[!IMPORTANT]": "Important", "[!NOTE]": "Note", "[!WARNING]": "Warning"}
                if marker in labels:
                    prefix = f"<b>{labels[marker]}</b><br/>"
                    children = children[1:]
                    if children and children[0].get("type") == "softbreak":
                        children = children[1:]
            contents.append(Paragraph(prefix + _inline(children), styles["quote"]))
        elif child_type == "block_code":
            contents.append(Preformatted(child.get("raw", "").rstrip(), styles["code"], maxLineLength=120))
    table = Table([[contents]], colWidths=[page_width], splitInRow=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("LINEBEFORE", (0, 0), (0, -1), 2, colors.HexColor("#64748b")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
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
            elif child.get("type") == "block_code":
                raw = child.get("raw", "").rstrip()
                if raw:
                    parts.append(Preformatted(raw, styles["code"], maxLineLength=120))
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
    text = _filtered_markdown_text(path)
    tokens = parser(text)
    flowables: list = []
    skipped_document_title = False

    for token in tokens:
        t = token.get("type")
        if t == "blank_line":
            continue
        if t == "heading":
            level = min(int(token.get("attrs", {}).get("level", 2)), 6)
            if level == 1 and not skipped_document_title:
                skipped_document_title = True
                continue
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
            flowables.append(
                _table_flowable(
                    token,
                    styles,
                    page_width,
                    page_height,
                    path,
                    include_images,
                    max_image_px,
                    image_quality,
                )
            )
            flowables.append(Spacer(1, 5))
        elif t == "block_quote":
            flowables.append(_block_quote_flowable(token, styles, page_width))
            flowables.append(Spacer(1, 5))
        elif t == "thematic_break":
            flowables.append(Spacer(1, 8))
        elif t == "block_html":
            raw = token.get("raw", "").strip()
            if raw and not raw.startswith("<!--"):
                flowables.append(Paragraph(html.escape(raw), styles["body"]))
        else:
            raise ValueError(f"unsupported Markdown block {t!r} in {path.relative_to(REPO_ROOT)}")
    return flowables

EUR_TO_USD = 1.0 / 0.92

def _simple_table(
    rows: list[list[str]],
    styles: dict[str, ParagraphStyle],
    page_width: float,
    *,
    header: bool = True,
) -> Table:
    table_rows = []
    for idx, row in enumerate(rows):
        style = styles["table_head"] if idx == 0 and header else styles["table"]
        table_rows.append([Paragraph(html.escape(cell), style) for cell in row])
    cols = max(len(row) for row in rows)
    col_width = page_width / cols
    table = Table(table_rows, colWidths=[col_width] * cols, repeatRows=1 if header else 0, splitInRow=1)
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]
    if header:
        commands.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")))
    table.setStyle(TableStyle(commands))
    return table

def _page_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.showOutline()
    canvas.setFont("BookSans" if "BookSans" in pdfmetrics.getRegisteredFontNames() else "Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawRightString(A4[0] - 1.5 * cm, 1.0 * cm, f"Page {doc.page}")
    canvas.drawString(1.5 * cm, 1.0 * cm, "OpenSourceRail documentation book")
    canvas.restoreState()

def primary_docs() -> list[Path]:
    return [REPO_ROOT/path for path in (
        'docs/open-source-rail-overview.md', 'engineering/ferrite_maglev/README.md',
        'crates/osr-maglev-control/README.md', 'docs/ARCHITECTURE.md', 'docs/ROADMAP.md')]

def primary_images() -> list[tuple[Path, str]]:
    base = REPO_ROOT/'docs/design-engine/ferrite-maglev'
    return [(base/name, label) for name, label in (
        ('baghdad-reference/station/overview.png', 'Partial six-car Baghdad station, magnetic guidebeams and island lift; acceptance remains open.'),
        ('native/interface/overview.png', 'Partial fixed magnetic interface; not a complete vehicle.'),
        ('beam-only/overview.png', 'Beam-only civil variant. Supports are envelopes; evacuation acceptance remains open.'),
        ('system-development/entry/overview.png', 'Partial evacuation entry frame and empty cassette. No deployed or stowed mechanism is qualified.'),
        ('system-development/compact-support/overview.png', 'Compact pier and foundation envelope. Site capacity and structural acceptance remain open.'))]

def primary_book_sources() -> dict[str, str]:
    paths = primary_docs()+[Path(__file__), REPO_ROOT/'tools/automation/generate-public-overview.py',
        REPO_ROOT/'OpenSourceRail maglev station concept.png', REPO_ROOT/'engineering/ferrite_maglev/city-index.json',
        REPO_ROOT/'docs/design-engine/ferrite-maglev/reference/manifest.json']
    paths += [p for p, _ in primary_images()]
    return {p.relative_to(REPO_ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

def primary_book(out_path: Path, *, include_images: bool, max_image_px: int, image_quality: int, source_ref: str, check: bool=False) -> None:
    from engineering.ferrite_maglev import delivery, model
    delivery.verify()
    identity = primary_book_sources()
    options = dict(include_images=include_images, max_image_px=max_image_px, image_quality=image_quality, source_ref=source_ref)
    receipt_path = out_path.with_suffix('.receipt.json')
    if check:
        receipt = json.loads(receipt_path.read_text())
        if (receipt.get('schema') != 'osr-primary-reader-book/1' or receipt.get('source_sha256') != identity
                or receipt.get('options') != options or receipt.get('pdf_sha256') != hashlib.sha256(out_path.read_bytes()).hexdigest()
                or any(receipt.get(k) is not False for k in model.FLAGS)):
            raise ValueError('primary book sources, PDF or receipt differ')
        return
    IMAGE_ERRORS.clear()
    _register_fonts()
    styles = _styles()
    width, height = A4
    content_width, content_height = width-2.9*cm-12, height-3.1*cm-12
    story = [Spacer(1, 3*cm), Paragraph('OpenSourceRail v0.5', styles['title']),
        Paragraph('Ferrite PM maglev — primary design reader edition', styles['subtitle']),
        Paragraph('Fixed magnetic modules · compact elevated guidebeams · Rust controls · local manufacture', styles['subtitle']),
        Paragraph('Provisional digital studies. Complete vehicle, civil and software qualification remains open. Accepted physical releases: 0.', styles['body']), PageBreak()]
    for number, path in enumerate(primary_docs()):
        title = path.read_text().splitlines()[0].lstrip('# ')
        story.extend([_outline_heading(title, styles['part'], 'primary-'+str(number), 0),
            Paragraph(html.escape(path.relative_to(REPO_ROOT).as_posix()), styles['source'])])
        story.extend(_render_markdown(path, styles, content_width, content_height, max_image_px, image_quality, include_images))
        story.append(PageBreak())
    story.append(_outline_heading('Native geometry review', styles['part'], 'native-review', 0))
    if include_images:
        for path, label in primary_images():
            story.extend(_image_flowables(dict(attrs=dict(url=str(path)), children=[dict(type='text', raw=label)]),
                path, styles, max_width=content_width, max_height=content_height*.55, max_px=max_image_px, quality=image_quality))
            story.append(Paragraph(label, styles['body']))
    index = json.loads((REPO_ROOT/'engineering/ferrite_maglev/city-index.json').read_text())
    story.extend([PageBreak(), _outline_heading('Primary maglev city directory', styles['part'], 'primary-cities', 0),
        Paragraph('Separate planning packages. Complete programme costs, local content, land and physical acceptance remain open for every city.', styles['body'])])
    rows = [['City', 'Provisional trainsets', 'Cars', 'Open gates']]
    rows += [[r['name'], str(r['trainsets']), str(r['cars']), str(r['open_gate_count'])] for r in index['cities']]
    story.append(_simple_table(rows, styles, content_width, header=True))
    if IMAGE_ERRORS:
        raise ValueError('primary book image errors: '+str(IMAGE_ERRORS))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = out_path.with_suffix('.pending.pdf')
    doc = BookDocTemplate(str(temporary), pagesize=A4, rightMargin=1.45*cm, leftMargin=1.45*cm,
        topMargin=1.55*cm, bottomMargin=1.55*cm, title='OpenSourceRail v0.5 — ferrite PM maglev', author='OpenSourceRail', invariant=True, pageCompression=1)
    doc.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)
    if identity != primary_book_sources():
        temporary.unlink()
        raise ValueError('primary book sources changed during rendering')
    temporary.replace(out_path)
    receipt = dict(schema='osr-primary-reader-book/1', source_sha256=identity, options=options,
        pdf_sha256=hashlib.sha256(out_path.read_bytes()).hexdigest(), **model.FLAGS)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')


def main() -> int:
    global REPOSITORY_BLOB_URL
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT, help='Output PDF path.')
    parser.add_argument('--check', action='store_true', help='Check PDF and source receipt without rendering.')
    parser.add_argument('--source-ref', default='main')
    parser.add_argument('--no-images', action='store_true')
    parser.add_argument('--max-image-px', type=int, default=900)
    parser.add_argument('--image-quality', type=int, default=60)
    parser.add_argument('--list-sources', action='store_true')
    args = parser.parse_args()
    if args.max_image_px < 32 or not 1 <= args.image_quality <= 95:
        parser.error('image size must be at least 32 px and quality between 1 and 95')
    REPOSITORY_BLOB_URL = 'https://github.com/modernecotech/OpenSourceRail/blob/' + quote(args.source_ref, safe='')
    os.chdir(REPO_ROOT)
    if args.list_sources:
        for path in primary_book_sources():
            print('primary\t'+path)
    else:
        primary_book(args.out, include_images=not args.no_images, max_image_px=args.max_image_px,
            image_quality=args.image_quality, source_ref=args.source_ref, check=args.check)
        print(args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
