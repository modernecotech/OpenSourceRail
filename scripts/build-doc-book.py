#!/usr/bin/env python3
"""Build the complete OpenSourceRail reader-edition documentation book.

The explicit source manifest includes canonical project, technical, software,
hardware, engineering, and high-level manufacturing documentation; developing-
country planning briefs; and a concise generated brief for every city model.
Generated indexes and detailed machine/shop records remain linked source data
rather than duplicated book chapters.

The renderer is intentionally self-contained. The repo image set is large,
so local images are downsampled into build/doc-book-assets before being
embedded in the PDF.
"""

from __future__ import annotations

import argparse
import html
import io
import os
import re
import tomllib
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

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


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = REPO_ROOT / "OpenSourceRail-Book.pdf"
ASSET_CACHE = REPO_ROOT / "build" / "doc-book-assets"
IMAGE_ERRORS: list[str] = []
REPOSITORY_BLOB_URL = "https://github.com/modernecotech/OpenSourceRail/blob/main"


@dataclass(frozen=True)
class SourceDoc:
    path: Path
    title: str
    part: str


@dataclass(frozen=True)
class CityModel:
    path: Path
    region: str
    country_name: str
    city_dir: str
    name: str
    iso: str
    population: int
    family: str
    lines: int
    stations: int
    route_km: float
    fleet: int
    coverage: float
    capex: float
    capex_per_km: float
    map_path: Path | None
    line_rows: tuple[tuple[str, str, str, str, str], ...]


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


def _doc_sources() -> list[SourceDoc]:
    docs: list[SourceDoc] = []

    def add(part: str, paths: list[Path]) -> None:
        for path in paths:
            docs.append(SourceDoc(path, _markdown_title(path), part))

    add(
        "Front Matter",
        [
            REPO_ROOT / "README.md",
            REPO_ROOT / "CONTRIBUTING.md",
            REPO_ROOT / "GOVERNANCE.md",
            REPO_ROOT / "CHANGELOG.md",
            REPO_ROOT / "LICENSE.md",
            REPO_ROOT / "LICENSES/README.md",
        ],
    )

    technical_docs = [
        path
        for path in _markdown_under("docs")
        if path.relative_to(REPO_ROOT).as_posix()
        not in {"docs/README.md", "docs/INDEX.md"}
    ]
    add("Architecture, Planning and Operations", technical_docs)

    software_docs: list[Path] = []
    for relative in ("crates", "deployment", "lib", "projects", "tools"):
        software_docs.extend(_markdown_under(relative))
    software_docs.append(REPO_ROOT / "scripts/README.md")
    add("Software, Deployment and Developer Tools", sorted(software_docs))

    engineering_docs: list[Path] = []
    for relative in ("engineering", "formal", "hardware"):
        engineering_docs.extend(_markdown_under(relative))
    add("Engineering, Hardware and Formal Assurance", sorted(engineering_docs))

    mechanical_docs = [REPO_ROOT / "mechanical-py/README.md"]
    for relative in (
        "mechanical-py/catalog",
        "mechanical-py/catalog/buildable-stations",
        "mechanical-py/catalog/buildable-trainset",
        "mechanical-py/catalog/design-system",
        "mechanical-py/catalog/fea",
        "mechanical-py/catalog/freecad",
        "mechanical-py/catalog/modular-fiberglass-body",
    ):
        mechanical_docs.extend(_markdown_under(relative, recursive=False))
    add("Mechanical Design and Manufacturing", sorted(set(mechanical_docs)))

    country_briefs = [
        path
        for path in sorted((REPO_ROOT / "designs").glob("*/*/NATIONAL-BRIEF.md"))
        if path.relative_to(REPO_ROOT / "designs").parts[0] != "europe"
    ]
    add("Developing-Country Planning Briefs", country_briefs)

    _validate_doc_sources(docs)
    return docs


def _markdown_under(relative: str, *, recursive: bool = True) -> list[Path]:
    root = REPO_ROOT / relative
    pattern = "**/*.md" if recursive else "*.md"
    return sorted(
        path
        for path in root.glob(pattern)
        if path.is_file()
        and not any(part.startswith(".") for part in path.relative_to(root).parts)
    )


def _markdown_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).replace("`", "")
    return path.relative_to(REPO_ROOT).as_posix()


def _validate_doc_sources(docs: list[SourceDoc]) -> None:
    relative = [source.path.relative_to(REPO_ROOT).as_posix() for source in docs]
    if len(relative) != len(set(relative)):
        duplicates = sorted(path for path, count in Counter(relative).items() if count > 1)
        raise ValueError(f"duplicate documentation-book sources: {duplicates}")
    missing = [path for path in relative if not (REPO_ROOT / path).is_file()]
    if missing:
        raise FileNotFoundError(f"missing documentation-book sources: {missing}")

    excluded = {"docs/README.md", "docs/INDEX.md", "designs/README.md"}
    accidentally_included = excluded.intersection(relative)
    detailed_records = [
        path
        for path in relative
        if "/definitions/" in path or "/travelers/" in path
    ]
    if accidentally_included or detailed_records:
        raise ValueError(
            "reader book includes generated navigation or detailed shop records: "
            f"{sorted(accidentally_included) + detailed_records}"
        )


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
    table = Table([[contents]], colWidths=[page_width])
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


def _load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def _quality_value(city_dir: Path, key: str) -> float:
    for path in city_dir.glob("*.design-quality.yaml"):
        match = re.search(rf"{re.escape(key)}:\s*([0-9.]+)", path.read_text(errors="ignore"))
        if match:
            return float(match.group(1))
    return 0.0


EUR_TO_USD = 1.0 / 0.92


def _usd(value: float) -> str:
    if value >= 1_000_000_000:
        return f"USD {value / 1_000_000_000:.2f}bn"
    return f"USD {value / 1_000_000:.0f}M"


def _city_models() -> list[CityModel]:
    models: list[CityModel] = []
    for design_path in sorted((REPO_ROOT / "designs").glob("*/*/*/design.toml")):
        city_dir = design_path.parent
        rel_parts = city_dir.relative_to(REPO_ROOT / "designs").parts
        # Lyon is retained in the repository as an engineering comparison, not
        # as evidence for the developing-world programme covered by the book.
        if rel_parts[0] == "europe":
            continue
        design = _load_toml(design_path)
        city = design.get("city", {})
        lines = design.get("lines", [])
        fleets = design.get("fleets", [])
        stations_by_line: dict[str, int] = {}
        for station in design.get("stations", []):
            line_name = str(station.get("line", ""))
            stations_by_line[line_name] = stations_by_line.get(line_name, 0) + 1
        fleet_by_line = {
            str(fleet.get("line", "")): int(fleet.get("trainset_count", 0))
            for fleet in fleets
        }
        route_km = sum(float(line.get("length_m", 0.0)) for line in lines) / 1000.0
        costs = design.get("costs", {})
        capex = float(costs.get("total_usd", float(costs.get("total_eur", 0.0)) * EUR_TO_USD))
        map_candidates = sorted(city_dir.glob("*-network-map.png"))
        line_rows = []
        for line in lines[:8]:
            line_name = str(line.get("name") or line.get("id") or "?")
            length = float(line.get("length_m", 0.0)) / 1000.0
            line_rows.append(
                (
                    line_name,
                    f"{length:.1f} km",
                    str(stations_by_line.get(line_name, "")),
                    str(fleet_by_line.get(line_name, "")),
                    str(line.get("shape", "")),
                )
            )
        models.append(
            CityModel(
                path=city_dir,
                region=rel_parts[0],
                country_name=rel_parts[1],
                city_dir=rel_parts[2],
                name=city.get("name") or rel_parts[2].replace("-", " "),
                iso=city.get("country", "??"),
                population=int(city.get("population", 0)),
                family=lines[0].get("rolling_stock", "?") if lines else "?",
                lines=len(lines),
                stations=len(design.get("stations", [])),
                route_km=route_km,
                fleet=sum(int(f.get("trainset_count", 0)) for f in fleets),
                coverage=_quality_value(city_dir, "high_demand_coverage"),
                capex=capex,
                capex_per_km=capex / route_km if route_km else 0.0,
                map_path=map_candidates[0] if map_candidates else None,
                line_rows=tuple(line_rows),
            )
        )
    return models


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
    table = Table(table_rows, colWidths=[col_width] * cols, repeatRows=1 if header else 0)
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


def _city_directory_flowables(
    models: list[CityModel],
    styles: dict[str, ParagraphStyle],
    page_width: float,
) -> list:
    by_region: dict[str, dict[str, int]] = {}
    for model in models:
        by_region.setdefault(model.region, {})
        by_region[model.region][model.country_name] = by_region[model.region].get(model.country_name, 0) + 1
    rows = [["Region", "Countries", "Cities"]]
    for region in sorted(by_region):
        countries = by_region[region]
        rows.append(
            [
                region,
                ", ".join(f"{country} ({count})" for country, count in sorted(countries.items())),
                str(sum(countries.values())),
            ]
        )
    return [
        Paragraph("City Model Directory", styles["h1"]),
        Paragraph(
            "City models are grouped as designs/<region>/<country>/<City>/. "
            "These generated city models are the source of truth for city-specific "
            "network, fleet, cost, and energy figures. RFCs and worked examples "
            "provide context or methods, not competing city plans. The book uses "
            "concise city briefs to avoid repeating the generated README boilerplate.",
            styles["body"],
        ),
        _simple_table(rows, styles, page_width),
        PageBreak(),
    ]


def _city_brief_flowables(
    model: CityModel,
    styles: dict[str, ParagraphStyle],
    page_width: float,
    page_height: float,
    max_image_px: int,
    image_quality: int,
    include_images: bool,
) -> list:
    rel = model.path.relative_to(REPO_ROOT).as_posix()
    rows = [
        ["Metric", "Value"],
        ["Path", rel],
        ["ISO / population", f"{model.iso} / {model.population:,}"],
        ["Family", model.family],
        ["Lines / stations", f"{model.lines} / {model.stations}"],
        ["Route length", f"{model.route_km:.1f} km"],
        ["Fleet", f"{model.fleet} trainsets"],
        ["High-demand coverage", f"{model.coverage:.0%}"],
        ["CAPEX", f"{_usd(model.capex)} ({_usd(model.capex_per_km)} / km)"],
    ]
    flows: list = [
        Paragraph(html.escape(f"Generated City Model - {model.name}"), styles["h2"]),
        Paragraph(html.escape(f"{model.region} / {model.country_name} / {model.city_dir}"), styles["small"]),
        _simple_table(rows, styles, page_width, header=True),
        Spacer(1, 5),
    ]
    if include_images and model.map_path:
        image_token = {"attrs": {"url": model.map_path.name}, "children": [{"type": "text", "raw": f"{model.name} network map"}]}
        flows.extend(
            _image_flowables(
                image_token,
                model.path / "README.md",
                styles,
                max_width=page_width,
                max_height=page_height * 0.24,
                max_px=max_image_px,
                quality=image_quality,
            )
        )
    if model.line_rows:
        flows.append(
            _simple_table(
                [["Line", "Length", "Stations", "Trainsets", "Shape"], *[list(row) for row in model.line_rows]],
                styles,
                page_width,
                header=True,
            )
        )
    return flows


def _page_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.showOutline()
    canvas.setFont("BookSans" if "BookSans" in pdfmetrics.getRegisteredFontNames() else "Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#64748b"))
    canvas.drawRightString(A4[0] - 1.5 * cm, 1.0 * cm, f"Page {doc.page}")
    canvas.drawString(1.5 * cm, 1.0 * cm, "OpenSourceRail documentation book")
    canvas.restoreState()


def _book_contents_flowables(
    docs: list[SourceDoc], city_models: list[CityModel], styles: dict[str, ParagraphStyle], page_width: float
) -> list:
    counts = Counter(source.part for source in docs)
    rows = [["Part", "Documents"]]
    rows.extend([[part, str(count)] for part, count in counts.items()])
    rows.append(["Generated City Model Briefs", str(len(city_models))])
    return [
        _outline_heading("Book Contents", styles["part"], "book-contents", 0),
        Paragraph(
            "Each source chapter prints its repository path. The city section is generated "
            "directly from each canonical design.toml model.",
            styles["body"],
        ),
        _simple_table(rows, styles, page_width, header=True),
        Spacer(1, 10),
        Paragraph("Reader-edition boundary", styles["h2"]),
        Paragraph(
            "This book includes canonical explanatory and review documentation. The generated "
            "Markdown inventory, duplicate city READMEs and catalogue tables, detailed component "
            "definitions, and signable shop travelers remain in the repository and are linked by "
            "their higher-level chapters; reproducing them here would duplicate source records.",
            styles["body"],
        ),
    ]


def build_pdf(out_path: Path, include_images: bool, max_image_px: int, image_quality: int) -> None:
    IMAGE_ERRORS.clear()
    _register_fonts()
    styles = _styles()
    docs = _doc_sources()
    city_models = _city_models()
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
            "Complete reader edition: project, technical, software, hardware, engineering, "
            "manufacturing, country-planning, and city-model documentation.",
            styles["subtitle"],
        ),
        Paragraph(
            f"Generated from {len(docs)} source documents and {len(city_models)} city models.",
            styles["subtitle"],
        ),
        PageBreak(),
    ]
    story.extend(_book_contents_flowables(docs, city_models, styles, content_width))
    story.append(PageBreak())

    current_part: str | None = None
    for idx, source in enumerate(docs):
        if idx > 0:
            story.append(PageBreak())
        if source.part != current_part:
            current_part = source.part
            story.append(
                _outline_heading(current_part, styles["part"], f"part-{idx}", 0)
            )
        rel = source.path.relative_to(REPO_ROOT).as_posix()
        story.append(
            _outline_heading(source.title, styles["h1"], f"document-{idx}", 1)
        )
        source_url = f"{REPOSITORY_BLOB_URL}/{quote(rel, safe='/')}"
        story.append(
            Paragraph(
                "Repository source: "
                f"<link href=\"{html.escape(source_url, quote=True)}\" color=\"#2563eb\">"
                f"<font name=\"Courier\">{html.escape(rel)}</font></link>",
                styles["source"],
            )
        )
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

    story.append(PageBreak())
    story.append(
        _outline_heading(
            "Generated City Models", styles["part"], "generated-city-models", 0
        )
    )
    story.extend(_city_directory_flowables(city_models, styles, content_width))
    current_region: str | None = None
    current_country: str | None = None
    for model in city_models:
        if model.region != current_region:
            if current_region is not None:
                story.append(PageBreak())
            current_region = model.region
            current_country = None
            story.append(
                _outline_heading(
                    model.region, styles["h1"], f"region-{model.region}", 1
                )
            )
        if model.country_name != current_country:
            current_country = model.country_name
            story.append(
                _outline_heading(
                    model.country_name,
                    styles["h2"],
                    f"country-{model.region}-{model.country_name}",
                    2,
                )
            )
        story.extend(
            _city_brief_flowables(
                model,
                styles,
                page_width=content_width,
                page_height=content_height,
                max_image_px=max_image_px,
                image_quality=image_quality,
                include_images=include_images,
            )
        )
        story.append(Spacer(1, 12))

    doc = BookDocTemplate(
        str(out_path),
        pagesize=A4,
        rightMargin=right,
        leftMargin=left,
        topMargin=top,
        bottomMargin=bottom,
        title="OpenSourceRail Documentation Book",
        author="OpenSourceRail",
        invariant=True,
        pageCompression=1,
    )
    if IMAGE_ERRORS:
        details = "\n".join(f"- {error}" for error in IMAGE_ERRORS)
        raise RuntimeError(f"documentation book has image errors:\n{details}")
    doc.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output PDF path.")
    parser.add_argument("--no-images", action="store_true", help="Skip local images.")
    parser.add_argument("--max-image-px", type=int, default=900, help="Maximum cached image dimension.")
    parser.add_argument("--image-quality", type=int, default=60, help="JPEG quality for cached images.")
    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="Print the validated reader-document and city-model manifest, then exit.",
    )
    args = parser.parse_args()

    os.chdir(REPO_ROOT)
    if args.list_sources:
        for source in _doc_sources():
            print(f"document\t{source.part}\t{source.path.relative_to(REPO_ROOT).as_posix()}")
        for model in _city_models():
            design_path = model.path / "design.toml"
            print(f"city\tGenerated City Model Briefs\t{design_path.relative_to(REPO_ROOT).as_posix()}")
        return 0
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
