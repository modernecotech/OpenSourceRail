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
CITY_CASES = (
    "west-asia/Iraq/Samawah", "west-asia/Iraq/Baghdad",
    "west-asia/Iraq/Basra", "west-asia/Iraq/Erbil",
    "west-asia/Jordan/Amman", "south-asia/Pakistan/Karachi",
    "east-africa/Kenya/Nairobi", "east-africa/Zambia/Lusaka",
    "latin-america/Ecuador/Cuenca",
    "latin-america/El Salvador/San-Salvador",
)
CITY_EVIDENCE = tuple(
    f"cities/catalogue/{city}/{name}"
    for city in CITY_CASES
    for name in ("README.md", "engineering/outline/network.svg")
)
PARTS = (
    ("I. An open railway for people", "Purpose, passenger experience and the design reference.", (
        ("A note to the reader", "docs/BOOK.md"),
        ("Why build an open railway", "docs/book/01-purpose.md"),
        ("The passenger journey", "docs/book/02-passenger.md"),
        ("A reference, with room to explore", "docs/book/03-architecture.md"),
        ("Capacity, frequency and useful service", "docs/book/19-service.md"),
        ("Three connected products", "docs/book/47-three-products.md"),
    )),
    ("II. The published v0.6.1 platform", "A guided tour of the released software and its limits.", (
        ("The published v0.6.1 platform", "docs/book/27-release-orientation.md"),
        ("A reader's first session", "docs/book/28-first-session.md"),
        ("Exploring the city atlas", "docs/book/29-city-atlas.md"),
        ("A Samawah Workbench journey", "docs/book/30-samawah-workbench.md"),
        ("Baghdad and retained comparisons", "docs/book/31-baghdad.md"),
        ("Exploring candidate research", "docs/book/32-candidate-lab.md"),
        ("CAD and engineering views", "docs/book/33-cad-gallery.md"),
        ("Reading costs and delivery drafts", "docs/book/34-cost-delivery-exports.md"),
        ("Business, supervision and controls", "docs/book/35-control-business.md"),
        ("What v0.6.1 does not claim", "docs/book/36-release-boundaries.md"),
    )),
    ("III. From city to corridor", "Planning, service and a worked station revision.", (
        ("From a city brief to an alignment", "docs/book/04-city.md"),
        ("Samawah: one edit through the system", "docs/book/05-samawah.md"),
        ("Networks, service and city variety", "docs/book/06-networks.md"),
        ("Stations and the streets around them", "docs/book/20-stations.md"),
    )),
    ("IV. Ten city route examples", "Calculated maps from different city contexts, with their planning limits.", (
        ("How to read a city route map", "docs/book/50-map-reading.md"),
        ("Samawah and Baghdad", "docs/book/51-iraq-samawah-baghdad.md"),
        ("Basra and Erbil", "docs/book/52-iraq-basra-erbil.md"),
        ("Amman and Karachi", "docs/book/53-amman-karachi.md"),
        ("Nairobi and Lusaka", "docs/book/54-nairobi-lusaka.md"),
        ("Cuenca and San Salvador", "docs/book/55-cuenca-san-salvador.md"),
    )),
    ("V. The physical railway", "Vehicle, passenger interfaces, power, stopping and civil works.", (
        ("Vehicle and running gear", "docs/book/07-vehicle.md"),
        ("Inside the vehicle", "docs/book/24-inside.md"),
        ("Doors, cabin and access", "docs/book/08-door.md"),
        ("Propulsion, power and braking", "docs/book/09-propulsion.md"),
        ("Stopping, faults and rescue", "docs/book/25-recovery.md"),
        ("Heat, ventilation and electrical life", "docs/book/21-systems.md"),
        ("Stations, structures and construction", "docs/book/10-civil.md"),
    )),
    ("VI. Product and assembly views", "Drawings and models of distinct railway research candidates.", (
        ("The train in engineering views", "docs/book/57-train-views.md"),
        ("Doors, seating and accessible interiors", "docs/book/58-door-and-interior.md"),
        ("Station drive and launch alternatives", "docs/book/59-station-drive-views.md"),
        ("Civil assemblies and construction", "docs/book/60-civil-gallery.md"),
        ("Manufacturing details and assembly", "docs/book/63-manufacturing-gallery.md"),
    )),
    ("VII. Making and keeping the railway", "Local production, whole-life decisions, control and maintenance.", (
        ("Local manufacture and sourcing", "docs/book/11-manufacture.md"),
        ("From factory to finished corridor", "docs/book/22-delivery.md"),
        ("Cost and whole-life decisions", "docs/book/12-cost.md"),
        ("A corridor cost comparison", "docs/book/26-benchmark.md"),
        ("Control and passenger protection", "docs/book/13-control.md"),
        ("Business, maintenance and renewal", "docs/book/14-lifecycle.md"),
    )),
    ("VIII. Digital twins and testing", "How models are connected, checked and challenged.", (
        ("A digital twin of one candidate", "docs/book/56-digital-twin.md"),
        ("What structural tests show", "docs/book/61-structural-tests.md"),
        ("Journey, control and fault tests", "docs/book/62-journey-tests.md"),
        ("What twin verification can and cannot prove", "docs/book/64-twin-assurance.md"),
    )),
    ("IX. Engineering and evidence", "What the tools establish and what remains open.", (
        ("Engineering tools and evidence", "docs/book/15-tools.md"),
        ("Current results and open questions", "docs/book/16-evidence.md"),
        ("Research choices and independent checks", "docs/book/23-research.md"),
    )),
    ("X. Building the continuous v0.7 project", "A corridor revision linked to design, manufacture and maintenance.", (
        ("The v0.7 continuous project", "docs/book/37-v07-continuity.md"),
        ("Samawah before and after", "docs/book/38-samawah-practice.md"),
        ("Native city editing with RustGIS", "docs/book/39-native-gis.md"),
        ("Door operator as a complete module", "docs/book/40-door-design.md"),
        ("New CAD and mechanics tools", "docs/book/41-structural.md"),
        ("Manufacture and maintenance custody", "docs/book/42-lifecycle-custody.md"),
        ("Efficient repeated studies", "docs/book/43-performance.md"),
        ("The Workbench project journey", "docs/book/44-workbench-journey.md"),
        ("Generalising to Baghdad", "docs/book/45-baghdad-next.md"),
        ("What completes v0.7", "docs/book/46-v07-readiness.md"),
        ("One complete candidate for v0.7", "docs/book/17-v07.md"),
    )),
    ("XI. The interfaces in use", "A visual tour of the Workbench, planning and parts views.", (
        ("The current Workbench", "docs/book/65-current-workbench.md"),
        ("Planning and maps on screen", "docs/book/66-planning-screen.md"),
        ("Parts and lifecycle on screen", "docs/book/67-parts-screen.md"),
        ("Reading status and holds", "docs/book/68-reading-status.md"),
    )),
    ("XII. Adoption and open knowledge", "Using the platform, contributing and reading deeper.", (
        ("Who can use the platform now", "docs/book/48-adoption.md"),
        ("Keeping the work open and useful", "docs/book/49-open-knowledge.md"),
        ("Sources, terms and licensing", "docs/book/18-sources.md"),
    )),
)
CHAPTERS = tuple(chapter for _, _, chapters in PARTS for chapter in chapters)
EVIDENCE_INPUTS = (
    "README.md", "CONTRIBUTING.md", "GOVERNANCE.md",
    "docs/platform-guide.md", "docs/ARCHITECTURE.md",
    "docs/first-adoptable-product.md", "docs/engineering-models/README.md",
    "docs/capabilities/README.md", "docs/ROADMAP.md",
    "docs/releases/v0.6.1/README.md", "docs/releases/v0.6.1/known-limitations.md",
    "docs/releases/v0.6.1/release-notes.md",
    "docs/releases/v0.6.1/feature-maturity.md",
    "docs/releases/v0.6.1/quickstart.md", "docs/releases/v0.6.1/demonstrations.md",
    "docs/design-engine/v07-project-continuity/README.md",
    "docs/design-engine/v07-execution/README.md",
    "docs/design-engine/vehicle-parts/README.md",
    "docs/design-engine/coupled-railway/README.md",
    "docs/design-engine/craft-backends/README.md",
    "docs/design-engine/digital-twin/README.md",
    "docs/design-engine/digital-twin/validation.md",
    "docs/design-engine/reconciled-pilot/README.md",
    "docs/design-engine/trip-dynamics/README.md",
    "docs/design-engine/launch-detail/README.md",
    "docs/design-engine/viaduct-backends/README.md",
    "docs/assets/engineering-gallery-v06/manifest.json",
    "docs/book/images/visual-provenance.json",
    "docs/design-engine/model-based-cost-and-delivery.md",
    "docs/integration/v06-platform.md", "docs/integration/v07-assembly-lifecycle.md",
    "docs/workbench/planning/README.md", "docs/gis/README.md",
    "docs/plans/v0.7-agent-delivery-plan.md",
    *CITY_EVIDENCE,
)
INPUTS = tuple(dict.fromkeys((
    "engineering/platform_book.py",
    "tools/automation/build-doc-book.py",  # Shared Markdown/PDF renderer; historical selection is not imported.
    "tools/automation/build-book-map-excerpts.py",
    HERO,
    "campaigns/v07-execution.json",
    "engineering/development-baseline.toml",
    *EVIDENCE_INPUTS,
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
        if (receipt.get("schema") != "osr-platform-ebook/3"
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
    styles["body"].fontSize = 10
    styles["body"].leading = 14
    styles["body"].spaceAfter = 7
    styles["small"].fontSize = 8
    styles["small"].leading = 11
    for name in ("table", "table_head"):
        styles[name].fontSize = 8
        styles[name].leading = 10
    content_width = A4[0] - 2.9 * cm - 12
    content_height = A4[1] - 3.1 * cm - 12
    story = [
        Spacer(1, 1.1 * cm),
        Paragraph("OpenSourceRail", styles["title"]),
        Paragraph("Open Engineering Platform", styles["subtitle"]),
        Paragraph("An illustrated guide to the railway, its people and its open engineering work",
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
                  Paragraph(f"{len(PARTS)} parts and {len(CHAPTERS)} chapters. "
                            "Use the PDF outline for direct chapter navigation. "
                            "The separate receipt records the exact sources and illustrations.",
                            styles["body"])))
    toc_index = 0
    for part_number, (part, description, chapters) in enumerate(PARTS, 1):
        story.append(Paragraph(
            f'<link href="#part-{part_number}"><b>{part}</b></link> - {description}',
            styles["body"]))
        for chapter_number, (title, _) in enumerate(chapters, 1):
            toc_index += 1
            story.append(Paragraph(
                f'<link href="#chapter-{toc_index}">{part_number}.{chapter_number} '
                f'{title}</link>', styles["small"]))
    chapter_index = 0
    for part_number, (part, description, chapters) in enumerate(PARTS, 1):
        story.extend((PageBreak(), render._outline_heading(part, styles["part"],
                                                           f"part-{part_number}", 0),
                      Paragraph(description, styles["subtitle"])))
        for chapter_number, (title, name) in enumerate(chapters, 1):
            chapter_index += 1
            story.extend((PageBreak(), render._outline_heading(
                f"{part_number}.{chapter_number} {title}", styles["h1"],
                f"chapter-{chapter_index}", 1)))
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
    record = dict(schema="osr-platform-ebook/3", role="human-readable-current-platform-and-engineering-ebook",
                  source_sha256=source, pdf_sha256=_digest(output), pages=pages,
                  **FLAGS)
    record["receipt_id"] = _identity(record)
    pending_receipt = receipt_path.with_suffix(".pending.json")
    pending_receipt.write_text(json.dumps(record, sort_keys=True, separators=(",", ":"),
                                          ensure_ascii=False) + "\n")
    pending_receipt.replace(receipt_path)
    return dict(verified=True, cached=False, pages=pages, **FLAGS)
