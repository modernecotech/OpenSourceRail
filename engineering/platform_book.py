"""Build the maintained platform reader without admitting the held dossier."""

from __future__ import annotations

from hashlib import sha256
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
BOOK = "OpenSourceRail-Book.pdf"
RECEIPT = "OpenSourceRail-Book.receipt.json"
SOURCE = "docs/BOOK.md"
HERO = "docs/images/v06/v06-hero-elevated-station.webp"
CHAPTERS = (
    ("Reader and scope", "docs/BOOK.md"),
    ("Project and products", "README.md"),
    ("Current capabilities", "docs/capabilities/README.md"),
    ("Published v0.6.1 software", "docs/releases/v0.6.1/README.md"),
    ("Published limitations", "docs/releases/v0.6.1/known-limitations.md"),
    ("v0.7 roadmap", "docs/ROADMAP.md"),
)
INPUTS = (
    "engineering/platform_book.py",
    "tools/automation/build-doc-book.py",  # Shared Markdown/PDF renderer; historical selection is not imported.
    SOURCE,
    HERO,
    "README.md",
    "docs/README.md",
    "docs/ARCHITECTURE.md",
    "docs/ROADMAP.md",
    "docs/capabilities/README.md",
    "docs/releases/v0.6.1/README.md",
    "docs/releases/v0.6.1/known-limitations.md",
    "docs/design-engine/v07-execution/README.md",
    "docs/plans/v0.7-agent-delivery-plan.md",
    "campaigns/v07-execution.json",
    "engineering/development-baseline.toml",
)
FLAGS = dict(engineering_accepted=False, physical_accepted=False,
             manufacturing_release=False, operating_release=False)


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _identity(value: dict) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False).encode()).hexdigest()


def _inputs(root: Path) -> dict[str, str]:
    return {name: _digest(root / name) for name in INPUTS}


def _renderer(root: Path):
    path = root / "tools/automation/build-doc-book.py"
    spec = importlib.util.spec_from_file_location("osr_book_markdown_renderer", path)
    if spec is None or spec.loader is None:
        raise ValueError("Book Markdown renderer unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.REPO_ROOT = root
    module.ASSET_CACHE = root / "build/doc-book-assets"
    return module


def _pages(path: Path) -> int:
    info = subprocess.check_output(["pdfinfo", str(path)], text=True)
    found = re.search(r"^Pages:\s+(\d+)$", info, re.MULTILINE)
    if found is None:
        raise ValueError("PDF page count unavailable")
    return int(found.group(1))


def _cover_image(path: Path) -> Image:
    from PIL import Image as PillowImage
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import Image

    with PillowImage.open(path) as source:
        source.thumbnail((1300, 900))
        stream = io.BytesIO()
        source.convert("RGB").save(stream, format="JPEG", quality=80, optimize=True)
    stream.seek(0)
    picture = Image(stream)
    width = A4[0] - 3.0 * cm
    picture.drawWidth = width
    picture.drawHeight = width * picture.imageHeight / picture.imageWidth
    return picture


def build(root: Path = ROOT, output: Path | None = None, *, check: bool = False) -> dict:
    root = Path(root).resolve()
    output = root / BOOK if output is None else Path(output)
    receipt_path = root / RECEIPT
    source = _inputs(root)
    if check:
        receipt = json.loads(receipt_path.read_bytes())
        expected = {k: v for k, v in receipt.items() if k != "receipt_id"}
        if (receipt.get("schema") != "osr-platform-reader/1"
                or receipt.get("source_sha256") != source
                or receipt.get("pdf_sha256") != _digest(output)
                or receipt.get("pages") != _pages(output)
                or any(receipt.get(k) is not v for k, v in FLAGS.items())
                or receipt.get("receipt_id") != _identity(expected)):
            raise ValueError("Platform book sources, PDF or receipt differ")
        return dict(verified=True, cached=True, pages=receipt["pages"], **FLAGS)

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import PageBreak, Paragraph, Spacer

    render = _renderer(root)
    render._register_fonts()
    styles = render._styles()
    for name in ("table", "table_head"):
        styles[name].fontSize = 7.2
        styles[name].leading = 9
    content_width = A4[0] - 2.9 * cm - 12
    content_height = A4[1] - 3.1 * cm - 12
    story = [
        Spacer(1, 1.1 * cm),
        Paragraph("OpenSourceRail", styles["title"]),
        Paragraph("Open Engineering Platform", styles["subtitle"]),
        Paragraph("Published v0.6.1 software  |  v0.7 development reader",
                  styles["subtitle"]),
        Spacer(1, 0.5 * cm),
        _cover_image(root / HERO),
        Spacer(1, 0.4 * cm),
        Paragraph("Wheel-supported reference and candidate-bound research. "
                  "Manufacturing, physical and operating acceptance remain open.",
                  styles["body"]),
    ]
    for number, (title, name) in enumerate(CHAPTERS):
        story.extend((PageBreak(), render._outline_heading(title, styles["part"],
                                                           f"chapter-{number}", 0),
                      Paragraph(name, styles["source"])))
        story.extend(render._render_markdown(root / name, styles, content_width,
                                            content_height, 1000, 70, False))
    temporary = output.with_suffix(".pending.pdf")
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        pdf = render.BookDocTemplate(str(temporary), pagesize=A4,
                                     rightMargin=1.45 * cm, leftMargin=1.45 * cm,
                                     topMargin=1.55 * cm, bottomMargin=1.55 * cm,
                                     title="OpenSourceRail - Open Engineering Platform",
                                     author="OpenSourceRail", invariant=True,
                                     pageCompression=1)
        pdf.build(story, onFirstPage=render._page_footer,
                  onLaterPages=render._page_footer)
        if source != _inputs(root):
            raise ValueError("Platform book sources changed during rendering")
        pages = _pages(temporary)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    record = dict(schema="osr-platform-reader/1", role="current-software-and-research-reader",
                  source_sha256=source, pdf_sha256=_digest(output), pages=pages,
                  **FLAGS)
    record["receipt_id"] = _identity(record)
    pending_receipt = receipt_path.with_suffix(".pending.json")
    pending_receipt.write_text(json.dumps(record, sort_keys=True, separators=(",", ":"),
                                          ensure_ascii=False) + "\n")
    pending_receipt.replace(receipt_path)
    return dict(verified=True, cached=False, pages=pages, **FLAGS)
