"""Build the illustrated, source-bound platform and engineering ebook."""

from __future__ import annotations

from hashlib import sha256
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
BOOK = "OpenSourceRail-Book.pdf"
RECEIPT = "OpenSourceRail-Book.receipt.json"
SOURCE = "docs/BOOK.md"
HERO = "docs/images/v06/v06-hero-elevated-station.webp"
PARTS = (
    ("I. Purpose and platform", "The project, its three products, candidate identities and current capabilities.", (
        ("Scope and reading guide", "docs/BOOK.md"),
        ("Platform and railway concept", "docs/platform-guide.md"),
        ("Architecture and evidence boundaries", "docs/ARCHITECTURE.md"),
        ("Capability register", "docs/capabilities/README.md"),
    )),
    ("II. Published software and adoption", "What v0.6.1 ships, what remains open and how a user starts.", (
        ("Published v0.6.1 release", "docs/releases/v0.6.1/README.md"),
        ("Installation and Samawah demonstration", "docs/releases/v0.6.1/quickstart.md"),
        ("Feature maturity", "docs/releases/v0.6.1/feature-maturity.md"),
        ("Known limitations", "docs/releases/v0.6.1/known-limitations.md"),
        ("First adoption path", "docs/first-adoptable-product.md"),
    )),
    ("III. City and corridor", "A candidate-bound Samawah revision, native GIS and city evidence.", (
        ("Samawah project continuity", "docs/design-engine/v07-project-continuity/README.md"),
        ("Editable city GIS", "docs/gis/README.md"),
        ("City design dossiers", "docs/design-engine/city-dossiers/README.md"),
    )),
    ("IV. Railway and engineering", "Vehicle, civil, propulsion, manufacture and numerical-method evidence.", (
        ("Coordinated railway experiment", "docs/design-engine/coupled-railway/README.md"),
        ("Vehicle parts and assembly", "docs/design-engine/vehicle-parts/README.md"),
        ("Engineering model gallery", "docs/engineering-models/README.md"),
        ("Current engineering interfaces", "docs/design-engine/engineering-closure/README.md"),
        ("CAD and FEA backends", "docs/design-engine/craft-backends/README.md"),
        ("Retained v0.6 engineering findings", "docs/design-engine/v06-design-closure/README.md"),
    )),
    ("V. Cost and lifecycle", "From candidate quantities to production, delivery and bounded business integration.", (
        ("Model-based cost and delivery", "docs/design-engine/model-based-cost-and-delivery.md"),
        ("Business platform integration", "docs/integration/v06-platform.md"),
    )),
    ("VI. v0.7 evidence and next work", "Measured progress, unresolved interfaces and the delivery programme.", (
        ("v0.7 execution and evidence", "docs/design-engine/v07-execution/README.md"),
        ("Roadmap", "docs/ROADMAP.md"),
        ("Agent delivery and tool migration plan", "docs/plans/v0.7-agent-delivery-plan.md"),
    )),
)
CHAPTERS = tuple(chapter for _, _, chapters in PARTS for chapter in chapters)
INPUTS = tuple(dict.fromkeys((
    "engineering/platform_book.py",
    "tools/automation/build-doc-book.py",  # Shared Markdown/PDF renderer; historical selection is not imported.
    HERO,
    "campaigns/v07-execution.json",
    "engineering/development-baseline.toml",
    *(name for _, name in CHAPTERS),
)))
FLAGS = dict(engineering_accepted=False, physical_accepted=False,
             manufacturing_release=False, operating_release=False)


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _identity(value: dict) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False).encode()).hexdigest()


def _inputs(root: Path) -> dict[str, str]:
    names = set(INPUTS)
    for _, name in CHAPTERS:
        for url in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", (root / name).read_text()):
            target = unquote(url.split(" ", 1)[0].split("#", 1)[0])
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            path = ((root / name).parent / target).resolve()
            try:
                names.add(path.relative_to(root).as_posix())
            except ValueError as exc:
                raise ValueError(f"Book image outside source tree: {name}: {url}") from exc
    return {name: _digest(root / name) for name in sorted(names)}


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
        if (receipt.get("schema") != "osr-platform-ebook/2"
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
    render.IMAGE_ERRORS.clear()
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
        Paragraph("Comprehensive illustrated edition | v0.6.1 published software | v0.7 development",
                  styles["subtitle"]),
        Spacer(1, 0.5 * cm),
        _cover_image(root / HERO),
        Spacer(1, 0.4 * cm),
        Paragraph("Wheel-supported reference and candidate-bound research. "
                  "Manufacturing, physical and operating acceptance remain open.",
                  styles["body"]),
    ]
    story.extend((PageBreak(), render._outline_heading("Contents", styles["part"],
                                                      "contents", 0),
                  Paragraph("Six parts and twenty-three source-attributed chapters. "
                            "Use the PDF outline for direct chapter navigation. "
                            "Each chapter keeps the evidence limits stated in its source.",
                            styles["body"])))
    for part_number, (part, description, chapters) in enumerate(PARTS, 1):
        story.append(Paragraph(f"<b>{part}</b> - {description}", styles["body"]))
        for chapter_number, (title, _) in enumerate(chapters, 1):
            story.append(Paragraph(f"{part_number}.{chapter_number} {title}", styles["small"]))
    chapter_index = 0
    for part_number, (part, description, chapters) in enumerate(PARTS, 1):
        story.extend((PageBreak(), render._outline_heading(part, styles["part"],
                                                           f"part-{part_number}", 0),
                      Paragraph(description, styles["subtitle"])))
        for chapter_number, (title, name) in enumerate(chapters, 1):
            chapter_index += 1
            story.extend((PageBreak(), render._outline_heading(
                f"{part_number}.{chapter_number} {title}", styles["h1"],
                f"chapter-{chapter_index}", 1), Paragraph(name, styles["source"])))
            story.extend(render._render_markdown(root / name, styles, content_width,
                                                content_height, 1200, 76, True))
    if render.IMAGE_ERRORS:
        raise ValueError("Book images could not be rendered: " + "; ".join(render.IMAGE_ERRORS))
    temporary = output.with_suffix(".pending.pdf")
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        pdf = render.BookDocTemplate(str(temporary), pagesize=A4,
                                     rightMargin=1.45 * cm, leftMargin=1.45 * cm,
                                     topMargin=1.55 * cm, bottomMargin=1.55 * cm,
                                     title="OpenSourceRail - Comprehensive Open Engineering Ebook",
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
    record = dict(schema="osr-platform-ebook/2", role="comprehensive-current-platform-and-engineering-ebook",
                  source_sha256=source, pdf_sha256=_digest(output), pages=pages,
                  **FLAGS)
    record["receipt_id"] = _identity(record)
    pending_receipt = receipt_path.with_suffix(".pending.json")
    pending_receipt.write_text(json.dumps(record, sort_keys=True, separators=(",", ":"),
                                          ensure_ascii=False) + "\n")
    pending_receipt.replace(receipt_path)
    return dict(verified=True, cached=False, pages=pages, **FLAGS)
