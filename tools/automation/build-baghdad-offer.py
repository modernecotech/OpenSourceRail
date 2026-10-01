#!/usr/bin/env python3
"""Build the evidence-linked Baghdad concept/FEED offer PDF."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
import tomllib

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
CITY = ROOT / "cities/catalogue/west-asia/Iraq/Baghdad"
OFFER = CITY / "offer"
PDF = OFFER / "Baghdad-OpenSourceRail-System-Offer.pdf"
MANIFEST = OFFER / "manifest.json"
TODAY = date(2026, 10, 1)

NAVY = colors.HexColor("#102936")
TEAL = colors.HexColor("#0A8175")
MINT = colors.HexColor("#E8F3EF")
PALE = colors.HexColor("#F3F7F5")
AMBER = colors.HexColor("#B86B08")
RED = colors.HexColor("#9F2D2D")
INK = colors.HexColor("#172128")
GREY = colors.HexColor("#52616A")


def read_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def money(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f} bn"
    return f"${value / 1_000_000:.0f} M"


class InvariantCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        kwargs["invariant"] = 1
        super().__init__(*args, **kwargs)


def register_fonts() -> tuple[str, str]:
    regular = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    bold = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("OSR", regular))
        pdfmetrics.registerFont(TTFont("OSR-Bold", bold))
        return "OSR", "OSR-Bold"
    return "Helvetica", "Helvetica-Bold"


FONT, FONT_BOLD = register_fonts()
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    "OfferTitle", fontName=FONT_BOLD, fontSize=27, leading=31,
    textColor=colors.white, alignment=TA_LEFT, spaceAfter=7 * mm,
))
styles.add(ParagraphStyle(
    "OfferSub", fontName=FONT, fontSize=12, leading=17,
    textColor=colors.HexColor("#D9ECE8"), spaceAfter=5 * mm,
))
styles.add(ParagraphStyle(
    "H1x", fontName=FONT_BOLD, fontSize=20, leading=24,
    textColor=NAVY, spaceAfter=5 * mm,
))
styles.add(ParagraphStyle(
    "H2x", fontName=FONT_BOLD, fontSize=12.5, leading=16,
    textColor=TEAL, spaceBefore=2 * mm, spaceAfter=2 * mm,
))
styles.add(ParagraphStyle(
    "Bodyx", fontName=FONT, fontSize=8.7, leading=12.1,
    textColor=INK, spaceAfter=2.4 * mm,
))
styles.add(ParagraphStyle(
    "Smallx", fontName=FONT, fontSize=7, leading=9.5,
    textColor=GREY, spaceAfter=1.5 * mm,
))
styles.add(ParagraphStyle(
    "Calloutx", fontName=FONT_BOLD, fontSize=9, leading=12.5,
    textColor=NAVY, spaceAfter=0,
))
styles.add(ParagraphStyle(
    "CardNum", fontName=FONT_BOLD, fontSize=18, leading=21,
    textColor=NAVY, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    "CardLabel", fontName=FONT, fontSize=7.2, leading=9,
    textColor=GREY, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    "CoverCard", fontName=FONT_BOLD, fontSize=13, leading=16,
    textColor=colors.white, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    "TableHead", fontName=FONT_BOLD, fontSize=7.3, leading=9,
    textColor=colors.white,
))
styles.add(ParagraphStyle(
    "TableCell", fontName=FONT, fontSize=7, leading=9,
    textColor=INK,
))


def p(text: str, style: str = "Bodyx") -> Paragraph:
    return Paragraph(text, styles[style])


def section(title: str, kicker: str | None = None):
    items = []
    if kicker:
        items.append(p(kicker.upper(), "Smallx"))
    items.append(p(title, "H1x"))
    return items


def callout(text: str, colour=TEAL):
    table = Table([[p(text, "Calloutx")]], colWidths=[174 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.8, colour),
        ("LINEBEFORE", (0, 0), (0, -1), 4, colour),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def cards(entries: list[tuple[str, str]]):
    cells = []
    for value, label in entries:
        cells.append([[p(value, "CardNum")], [p(label, "CardLabel")]])
    row = [Table(cell, colWidths=[34 * mm]) for cell in cells]
    widths = [174 * mm / len(row)] * len(row)
    table = Table([row], colWidths=widths)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), MINT),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#B7D7CF")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def data_table(rows: list[list[str]], widths: list[float]):
    contents = [[p(cell, "TableHead") for cell in rows[0]]]
    contents.extend([[p(str(cell), "TableCell") for cell in row] for row in rows[1:]])
    table = Table(contents, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CCD6D2")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def fitted_image(path: Path, max_width=174 * mm, max_height=98 * mm):
    image = Image(str(path))
    scale = min(max_width / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    image.hAlign = "CENTER"
    return image


def bullet(items: list[str]):
    return [p(f"• {item}") for item in items]


def page_chrome(canv, doc):
    page = canv.getPageNumber()
    canv.saveState()
    canv.setFillColor(NAVY)
    canv.rect(0, A4[1] - 12 * mm, A4[0], 12 * mm, stroke=0, fill=1)
    canv.setFont(FONT_BOLD, 7.5)
    canv.setFillColor(colors.white)
    canv.drawString(18 * mm, A4[1] - 8 * mm, "OPENSOURCERAIL · BAGHDAD SYSTEM OFFER")
    canv.setFont(FONT, 7)
    canv.drawRightString(A4[0] - 18 * mm, A4[1] - 8 * mm, "CONCEPT / FEED · CONTROLLED PLANNING BASELINE")
    canv.setStrokeColor(colors.HexColor("#CAD5D1"))
    canv.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
    canv.setFillColor(GREY)
    canv.drawString(18 * mm, 8 * mm, "Generated 1 October 2026 · Verify manifest hashes before use")
    canv.drawRightString(A4[0] - 18 * mm, 8 * mm, f"Page {page}")
    canv.restoreState()


def cover_chrome(canv, doc):
    canv.saveState()
    canv.setFillColor(NAVY)
    canv.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    canv.restoreState()


def build() -> None:
    OFFER.mkdir(parents=True, exist_ok=True)
    design_path = CITY / "design.toml"
    with design_path.open("rb") as handle:
        design = tomllib.load(handle)
    finance = read_json(CITY / "engineering/finance/summary.json")
    energy = read_json(CITY / "engineering/energy/summary.json")
    simulation = read_json(CITY / "engineering/simulation/validation-summary.json")
    sumo = read_json(CITY / "engineering/sumo/summary.json")
    gis = read_json(CITY / "engineering/gis/summary.json")
    operations = read_json(CITY / "operations/baghdad-operations-manifest.json")
    project = read_json(CITY / "engineering/project-twin/summary.json")
    package = read_json(CITY / "package-manifest.json")

    assert design["city"]["slug"] == "baghdad"
    assert len(design["lines"]) == 9 and len(design["stations"]) == 182
    assert simulation["passed"] and simulation["resilience_passed"]
    assert len(simulation["resilience_cases"]) == 8
    assert sumo["passed"] and gis["passed"]
    assert package["package_status"] == "incomplete"
    assert package["failed_summaries"] == [
        "engineering/depot-scope/summary.json",
        "engineering/stabling/summary.json",
    ]

    length_km = sum(item["length_m"] for item in design["lines"]) / 1000
    fleet = sum(item["trainset_count"] for item in design["fleets"])
    civil_lengths = defaultdict(float)
    civil_counts = Counter()
    for item in design["civil_segments"]:
        civil_counts[item["class"]] += 1
        civil_lengths[item["class"]] += item["to_station_m"] - item["from_station_m"]
    scheduled = sum(line["scheduled_services"] for line in sumo["lines"])
    arrived = sum(line["arrived_services"] for line in sumo["lines"])
    capex = finance["capex_usd"]["reconciled_project_total"]
    ops_totals = operations["totals"]

    doc = BaseDocTemplate(
        str(PDF), pagesize=A4, title="OpenSourceRail Baghdad System Offer",
        author="OpenSourceRail", subject="Baghdad urban rail concept and FEED offer",
        leftMargin=18 * mm, rightMargin=18 * mm, topMargin=20 * mm, bottomMargin=17 * mm,
    )
    normal_frame = Frame(18 * mm, 17 * mm, 174 * mm, 260 * mm, id="normal")
    cover_frame = Frame(18 * mm, 18 * mm, 174 * mm, 261 * mm, id="cover")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover_frame], onPage=cover_chrome, autoNextPageTemplate="normal"),
        PageTemplate(id="normal", frames=[normal_frame], onPage=page_chrome),
    ])

    story = []
    story.extend([
        Spacer(1, 12 * mm),
        p("BAGHDAD · IRAQ", "OfferSub"),
        p("A city-scale railway,<br/>designed as a verifiable system", "OfferTitle"),
        p("Concept and front-end engineering design offer", "OfferSub"),
        fitted_image(CITY / "baghdad-network-map.png", 174 * mm, 112 * mm),
        Spacer(1, 6 * mm),
        Table([[p("9 lines", "CoverCard"), p("182 stations", "CoverCard"), p("516.5 km", "CoverCard"), p("831 trainsets", "CoverCard")]], colWidths=[43.5 * mm] * 4,
              style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#173F4D")),
                                ("BOX", (0, 0), (-1, -1), 0.5, TEAL),
                                ("INNERGRID", (0, 0), (-1, -1), 0.5, TEAL),
                                ("TOPPADDING", (0, 0), (-1, -1), 7),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 7)])),
        Spacer(1, 6 * mm),
        p("Prepared from source-locked open geospatial data, a deterministic city design, native railway simulation, independent SUMO timetable validation and a city-specific project/operations twin.", "OfferSub"),
        p("STATUS · PLANNING BASELINE — NOT CONSTRUCTION RELEASE · 1 OCTOBER 2026", "OfferSub"),
        PageBreak(),
    ])

    story += section("The proposition", "Executive summary")
    story += [
        p("OpenSourceRail offers Baghdad an owner-controlled way to move from city data to a buildable railway programme: route planning, topography and water screening, civil classification, fleet and energy sizing, timetable simulation, manufacturing/procurement planning, maintenance, ERP/HR workflows, SCADA boundaries and certification evidence all share one configuration baseline."),
        cards([
            (f"{length_km:.1f} km", "double-track route"),
            ("3 min", "peak headway"),
            ("2.28 M", "practical trips/day"),
            (money(capex), "planning CAPEX"),
        ]),
        Spacer(1, 4 * mm),
        callout("Decision requested: authorize a time-boxed owner-led data validation and FEED phase—not construction—then select one priority corridor and a surveyed depot/stabling solution.", TEAL),
        Spacer(1, 4 * mm),
        p("What Baghdad receives", "H2x"),
    ]
    story += bullet([
        "A reproducible nine-line network baseline with 182 stations, 23 interchanges and open GIS layers.",
        "A complete planning twin linking 1,862 assets to budget, procurement, QA, maintenance and operating records.",
        "A six-car battery-electric fleet concept with candidate CRRC components under competitive procurement.",
        "Deterministic simulation and standards/FMEA evidence that reruns when controlled design inputs change.",
        "A staged assurance route that prevents a planning model from being misrepresented as regulatory approval.",
    ])
    story += [
        p("What this document does not claim", "H2x"),
        p("It is not a bid from CRRC or any other manufacturer; not a demand forecast, land approval, utility agreement, geotechnical design, issued-for-construction package, safety certificate or financing commitment. Values remain planning screens until the named release gates close."),
        fitted_image(CITY / "engineering/screenshots/baghdad-qgis-engineering-map.png", 174 * mm, 78 * mm),
        p("City-specific QGIS/GDAL package: 9 corridors, 182 stations, 23 interchanges and 2,312 classified civil segments.", "Smallx"),
        PageBreak(),
    ]

    story += section("Network, terrain and civil concept", "Physical system")
    story += [
        cards([
            ("428.3 km", "at grade"),
            ("75.8 km", "elevated/viaduct"),
            ("12.4 km", "bridge screen"),
            ("19", "junction upgrades"),
        ]),
        Spacer(1, 3 * mm),
        p("The automated designer combines OpenStreetMap transport/building/water/protected-area data with open SRTM elevation and derived slope. It rejects stations predominantly over mapped water and raises likely bridge, terrain viaduct, tight-radius and complex-junction segments for engineering review."),
        data_table([
            ["Civil class", "Segments", "Screened length", "FEED closure"],
            ["At grade", str(civil_counts["at-grade"]), f"{civil_lengths['at-grade']/1000:.1f} km", "Survey, land, utilities, drainage, crossings"],
            ["Elevated / viaduct", str(civil_counts["elevated"]), f"{civil_lengths['elevated']/1000:.1f} km", "Vertical alignment, foundations, constructability, urban fit"],
            ["Bridge", str(civil_counts["bridge"]), f"{civil_lengths['bridge']/1000:.1f} km", "Hydrology/hydraulics, navigation, scour and authority approval"],
        ], [34 * mm, 24 * mm, 31 * mm, 85 * mm]),
        Spacer(1, 3 * mm),
        p("Station and operating layout", "H2x"),
        p("The plan includes 182 unique stations and 23 interchange complexes. Stations remain prohibited on mapped-water footprints in the automatic planner. Platform, access, evacuation, universal access, fire/life safety, utilities, traffic management and property interfaces require site-by-site G1 design evidence."),
        p("Depot and stabling status", "H2x"),
        callout("OPEN GATE · The design allocates 831 trainsets operationally, but physical overnight positions, track-by-track capacity, workshop circulation, power/fire separation, security and morning/evening moves are not yet surveyed. The current USD 8 M depot allowance is not reconciled and must not be treated as a final depot cost.", AMBER),
        Spacer(1, 3 * mm),
        p("Proposed FEED action: compare at least three land-backed depot/distributed-stabling options, freeze an operator-owned fleet deployment plan, then update civil, energy, programme and cost baselines together."),
        PageBreak(),
    ]

    full_run = next(run for run in simulation["runs"] if run["duration_s"] == 90_000)
    story += section("Service, fleet and energy", "Operating concept")
    story += [
        cards([
            ("05:30–02:00", "operating day"),
            ("751", "peak revenue fleet"),
            ("71 + 9", "spare + cold reserve"),
            ("3,952", "one-way trips/day"),
        ]),
        Spacer(1, 3 * mm),
        p(f"The full native run covers 90,000 seconds and {full_run['train_km']:,.0f} train-km with zero invariant violations. Eight degraded cases—including aged batteries, maximum HVAC load, charging-contact loss, grid outage, missed charges and charger conflict—pass the present software model. SUMO independently records {arrived}/{scheduled} planned validation services arriving."),
        fitted_image(CITY / "engineering/screenshots/baghdad-simulation-dashboard.png", 174 * mm, 74 * mm),
        p("Native two-hour evidence trace; the full service-day-plus-run-out and degraded cases are retained as hashed JSON evidence.", "Smallx"),
        data_table([
            ["Energy element", "Planning baseline", "Release boundary"],
            ["Traction demand", "2,053.8 GWh/year", "Calibrated vehicle/duty data and operator timetable"],
            ["Station/depot PV", f"{energy['pv_nameplate_kw']/1000:.1f} MW", "Surveyed roofs/sites, yield, structure, protection"],
            ["Stationary storage", f"{energy['storage_capacity_kwh']/1000:.0f} MWh", "Supplier product, fire strategy, degradation and duty"],
            ["Connected charging", f"{energy['connected_charging_power_kw']/1000:.0f} MW", "Grid/interface studies, selectivity and timetable conflicts"],
            ["Dedicated solar", "1,018.6 MW", "Land, connection, PPA/ownership and measured resource"],
        ], [40 * mm, 43 * mm, 91 * mm]),
        Spacer(1, 2 * mm),
        callout("The model's zero residual grid/PPA import is a planning result. It is not proof of islanded operability or an approved grid connection; operating energy is explicitly marked unvalidated.", AMBER),
        PageBreak(),
    ]

    story += section("Rolling stock with a candidate CRRC parts package", "Industrial system")
    story += [
        p("The proposed fleet is 831 OpenSourceRail six-car, 111 m battery-electric trainsets. The vehicle architecture, requirements, interfaces, FMEA, maintenance identities and acceptance gates remain owner-controlled. CRRC product families are included as candidate components because CRRC publicly lists traction and electrical control equipment and vehicle components—not because a supplier has been appointed."),
        data_table([
            ["Candidate package", "Potential CRRC scope", "Required acceptance evidence"],
            ["Traction", "PMSM motors; SiC/traction converters; auxiliary converters", "Duty-cycle sizing, efficiency map, thermal/EMC, HIL and first article"],
            ["Running gear", "Bogies, air springs, dampers and associated components", "Gauge/axle load, dynamics, fatigue, climate/dust and maintainability"],
            ["Interfaces", "Couplers/draft gear, brake equipment, train-network controls", "ICDs, braking case, cybersecurity, diagnostics, rescue and interoperability"],
            ["Passenger systems", "Passenger-information and equipment interfaces", "Accessibility, language/content, EMC, fire, software and fleet configuration"],
        ], [34 * mm, 63 * mm, 77 * mm]),
        Spacer(1, 3 * mm),
        p("Procurement and localisation controls", "H2x"),
    ]
    story += bullet([
        "Issue performance-based RFQs and accept multiple compliant examples; do not lock the design to an unqualified catalogue part.",
        "Freeze actual manufacturer, model, firmware, drawings, material declarations, test reports, warranties, spares and obsolescence plan at G2.",
        "Qualify local assembly, inspection, tooling, calibration, training and technology-transfer outcomes contractually—not by supplier nationality claims.",
        "Keep batteries, cooling/HVAC, traction, braking, bogies, doors, train control and rescue interfaces in one system integration baseline.",
    ])
    story += [
        callout("Supplier statement · No CRRC partnership, endorsement, quotation, selected product or configuration approval exists in this package. All sourcing is subject to competition, technical qualification, licensing, contract and authority acceptance.", RED),
        Spacer(1, 3 * mm),
        p("Primary public sources", "H2x"),
        p('<link href="https://www.crrcgc.cc/en/73_5129/73_6648/index.html">CRRC components overview</link> · <link href="https://www.crrcgc.cc/en/73_5129/73_6648/73_6652/fca468a4-2.html">vehicle components</link> · <link href="https://www.crrcgc.cc/en/73_5129/73_6648/73_6650/index.html">electric-control equipment</link> · <link href="https://www.crrcgc.cc/dldqen/130_7787/index.html">CRRC Dalian traction/control</link>', "Smallx"),
        PageBreak(),
    ]

    story += section("One digital operating and delivery system", "Project, ERP, SCADA and maintenance")
    story += [
        cards([
            (f"{ops_totals['assets']:,}", "controlled assets"),
            (f"{ops_totals['manufacturing_tasks']:,}", "manufacturing tasks"),
            (f"{ops_totals['manufacturing_materials']:,}", "material/BOM rows"),
            (f"{ops_totals['maintenance_tasks']:,}", "maintenance tasks"),
        ]),
        Spacer(1, 3 * mm),
        p("The Baghdad project twin connects engineering configuration to schedule, cash requirements, procurement candidates, QA gates, manufacturing verification, asset registers and preventive maintenance. ERPNext/Frappe remains the business-system boundary; supervision/SCADA observations are isolated from movement authority and protection functions."),
        fitted_image(OFFER / "screenshots/baghdad-operations-dashboard.png", 174 * mm, 74 * mm),
        p("Live Baghdad operations dataset rendered by the OpenSourceRail portal; screenshot captured from the local controlled bundle.", "Smallx"),
        p("AI-supported management—with human authority", "H2x"),
        p("A multi-model advisory council may draft reversible management actions and compare independent model ballots. Quorum, model diversity, dissent, evidence hashes and an operator attestation are recorded. The council cannot command trains or SCADA, override ATP/interlocking or braking, authorize safety release, hire/dismiss staff, commit money, sign contracts, approve payments or exercise legal authority."),
        callout("The management model is decision support, not an artificial legal officer. Named competent people remain accountable for every approval and operational authority.", TEAL),
        PageBreak(),
    ]

    story += section("Assurance built into every change", "Certification and authorization")
    story += [
        fitted_image(OFFER / "screenshots/baghdad-qa-gates.png", 174 * mm, 73 * mm),
        p("Baghdad QA-gate view: planned evidence is configuration-linked; a planned row is not an approval.", "Smallx"),
        data_table([
            ["Gate", "Purpose", "Minimum decision evidence", "Authority"],
            ["G0 · baseline", "Identity and provenance", "Version, source, applicability, checksum and owner", "Configuration control"],
            ["G1 · design", "Design assurance", "Requirements, standards, hazards/FMEA, calculations and interfaces", "Owner engineer / discipline leads"],
            ["G2 · qualify", "Actual implementation", "Supplier/product configuration, type/first-article tests and NCR closure", "QA + engineering + supplier"],
            ["G3 · integrate", "Installed system", "FAT/SAT, site/vehicle integration, degraded operation and training", "Operator / integrator / assessor"],
            ["G4 · authorize", "Independent/legal acceptance", "Independent assessment and competent authority decisions", "Named legal authorities"],
        ], [23 * mm, 36 * mm, 78 * mm, 37 * mm]),
        Spacer(1, 3 * mm),
        p("Current evidence position", "H2x"),
        p("The GIS package, cost/finance generator, native simulation including eight degraded cases, SUMO timetable validation and operations bundle pass their deterministic planning checks and have current hashes. The overall city package remains incomplete by design because two physical summaries—depot scope and stabling—have not passed release readiness."),
        callout("No simulation eliminates required physical testing. The digital twin reduces redesign risk by screening standards, interfaces and failure modes before fabrication, then binds physical evidence back to the exact configuration.", AMBER),
        PageBreak(),
    ]

    capital = finance["capex_usd"]
    story += section("Commercial planning and delivery route", "Programme and funding")
    story += [
        cards([
            (money(capex), "base planning total"),
            (money(capital["risk_envelope_15_percent"]), "+15% envelope"),
            (money(capital["risk_envelope_25_percent"]), "+25% envelope"),
            ("77.1%", "modelled local capital"),
        ]),
        Spacer(1, 3 * mm),
        data_table([
            ["Planning bucket", "Value", "Critical qualification"],
            ["Civil works", money(3_894_477_344), "Survey/land/utilities/geotechnical and detailed structures"],
            ["Stations", money(907_900_000), "Site fit, passenger/fire/accessibility and MEP design"],
            ["Rolling stock", money(1_396_080_000), "Competitive supplier offer, qualification and support"],
            ["Solar plant", money(814_868_712.49), "Land, grid, measured resource and commercial structure"],
            ["Depots", money(8_000_000), "Not reconciled; replace after depot/stabling FEED"],
            ["Other systems / EPC", money(capex - 3_894_477_344 - 907_900_000 - 1_396_080_000 - 814_868_712.49 - 8_000_000), "Control, charging, project services and integration"],
        ], [49 * mm, 32 * mm, 93 * mm]),
        Spacer(1, 3 * mm),
        fitted_image(OFFER / "screenshots/baghdad-project-twin.png", 174 * mm, 71 * mm),
        p(f"Baghdad project twin: {project['totals']['programme_working_days']:,} planning days, {project['totals']['critical_work_packages']:,} critical work packages and {project['totals']['pre_ntp_order_actions']:,} pre-NTP actions. Its status is explicitly “planning-digital-twin-not-construction-release”.", "Smallx"),
        p("The foreign-turnkey and localisation figures are sensitivities, not received bids. Land, taxes/duties, utility relocation, escalation, financing fees and the unresolved depot correction must be owner-defined before affordability or financing decisions."),
        PageBreak(),
    ]

    story += section("A controlled path from model to railway", "Proposed engagement")
    story += [
        data_table([
            ["Phase", "Indicative purpose", "Exit decision"],
            ["0 · Validate", "12–16 weeks: authority map, data room, demand/operations calibration, survey procurement, priority corridor and depot longlist", "Owner accepts requirements, evidence gaps and FEED scope"],
            ["1 · FEED", "Surveyed alignment, utilities/property, geotechnical/hydraulic work, depot/stabling options, system requirements, RAMS and cost/risk baseline", "G1 design baseline and independently reviewed business case"],
            ["2 · Procure/pilot", "Competitive component/works packages; supplier qualification; HIL/FAT; one priority corridor, depot and operating organisation", "G2/G3 evidence and restricted trial authority"],
            ["3 · Authorize/scale", "Independent assessment, trial operation, competence, emergency readiness, legal approvals and measured performance", "G4 passenger service authority, then controlled rollout"],
        ], [25 * mm, 104 * mm, 45 * mm]),
        Spacer(1, 4 * mm),
        p("Immediate owner decisions", "H2x"),
    ]
    story += bullet([
        "Name the legal project owner, transport operator interface, infrastructure authority, safety/regulatory route and independent assessor.",
        "Authorize a controlled data room and field-data plan; confirm Arabic/English document and operational requirements.",
        "Select the passenger-demand method, target fares/service policy and a representative priority corridor.",
        "Protect land for at least three depot/stabling alternatives before choosing a physical configuration.",
        "Approve performance-based market engagement for rolling stock components, energy, civil works and system integration.",
    ])
    story += [
        p("External gates before any construction release", "H2x"),
        callout("Surveyed alignment, property and utilities · calibrated demand and operator timetable · geotechnical, drainage, structural and fire acceptance · supplier-frozen battery, charger, traction and mechanical equipment · independently assessed safety case and competent legal authorization.", RED),
        Spacer(1, 5 * mm),
        p("Evidence and reproducibility", "H2x"),
        p("The offer PDF, design, GeoPackage, simulations, operations bundle and screenshots are retained in the Baghdad city package. `offer/manifest.json` records SHA-256 hashes for the PDF and its controlled inputs. Regenerate the city with `./osr city baghdad`, capture the portal with `node tools/automation/capture-city-offer.mjs`, and rebuild this document with `python3 tools/automation/build-baghdad-offer.py`."),
        p("OpenSourceRail · open engineering baseline · owner-controlled evidence · fail-closed release claims", "Calloutx"),
    ]

    doc.build(story, canvasmaker=InvariantCanvas)

    input_paths = [
        Path("tools/automation/build-baghdad-offer.py"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/offer/README.md"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/design.toml"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/package-manifest.json"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/engineering/finance/summary.json"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/engineering/energy/summary.json"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/engineering/gis/summary.json"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/engineering/simulation/validation-summary.json"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/engineering/sumo/summary.json"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/engineering/project-twin/summary.json"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/operations/baghdad-operations-manifest.json"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/baghdad-network-map.png"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/engineering/screenshots/baghdad-qgis-engineering-map.png"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/engineering/screenshots/baghdad-simulation-dashboard.png"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/offer/screenshots/baghdad-operations-dashboard.png"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/offer/screenshots/baghdad-project-twin.png"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/offer/screenshots/baghdad-qa-gates.png"),
    ]
    manifest = {
        "schema_version": "1.0",
        "city": "baghdad",
        "document_status": "concept-and-feed-offer-not-construction-release",
        "generated_on": TODAY.isoformat(),
        "inputs": {
            str(path): {"bytes": (ROOT / path).stat().st_size, "sha256": sha256(ROOT / path)}
            for path in input_paths
        },
        "output": {
            "path": str(PDF.relative_to(ROOT)),
            "bytes": PDF.stat().st_size,
            "sha256": sha256(PDF),
        },
        "open_release_gates": package["external_release_gates"],
        "failed_city_summaries": package["failed_summaries"],
        "supplier_statement": "CRRC is a candidate component source only; no partnership, endorsement, quotation, selected supplier or configuration approval is claimed.",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {PDF.relative_to(ROOT)} ({PDF.stat().st_size:,} bytes)")
    print(f"Wrote {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
