#!/usr/bin/env python3
"""Build the evidence-linked Baghdad concept/FEED offer PDF."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
import tomllib

from osr_scenario.network_readme import compute_stats, _energy_plan

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
TODAY = date.fromisoformat(tomllib.loads((ROOT / "lib/templates/iraq-funding.toml").read_text())["model"]["as_of"])

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
    canv.drawString(18 * mm, 8 * mm, f"Generated {TODAY:%d %B %Y} · Verify manifest hashes before use")
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
    assert design["lines"] and design["stations"]
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
    scenario = tomllib.loads((CITY / "baghdad.toml").read_text())
    stats = compute_stats(design, scenario, int(design["city"]["population"]))
    energy_plan = _energy_plan(design, scenario, stats)
    stations = stats.unique_station_count
    lines = len(design["lines"])
    interchanges = len(design["interchanges"])
    peak = sum(f["peak_count"] for f in design["fleets"])
    spares = sum(f["spare_count"] for f in design["fleets"])
    reserve = sum(f["cold_reserve_count"] for f in design["fleets"])
    buckets = {r["bucket"]: r["total_usd"] for r in finance["capex_usd"]["procurement_origin_buckets"]}
    funding = finance["structured_financing"]
    assert funding["schedule_status"] == "linked-to-budget-work-packages"
    programme = json.loads((CITY.parent / "finance/baghdad-programme.json").read_text())
    comparison = programme["comparison"]
    independent = programme["independent_recalculation"]
    reconciliation = independent["reconciliation"]
    receipts = programme["operating_receipts"]
    fx = funding["assumptions"]["model"]["iqd_per_usd"]
    indexed = independent["cases"]["fare_5pct_opex_5pct"]
    indexed_prices = independent["fare_pricing"]["fare_5pct_opex_5pct"]
    offer_readme = OFFER / "README.md"
    text = offer_readme.read_text()
    system = f"""## Proposed system

The current planning baseline contains {lines} lines, {length_km:.1f} km of
double-track route, {stations} unique stations, {interchanges} interchange
complexes and {fleet} six-car trainsets. The service plan targets a three-minute
peak headway and a 05:30–02:00 operating day. The civil screen identifies
{civil_lengths['at-grade']/1000:.1f} km at grade,
{civil_lengths['elevated']/1000:.1f} km elevated and
{civil_lengths['bridge']/1000:.1f} km of bridge works. Open geospatial screening
must be confirmed by survey, property, utilities, ground, hydraulic and alignment
evidence during FEED.

The energy concept includes {energy['pv_nameplate_kw']/1000:.1f} MW of station/depot
PV, {energy['storage_capacity_kwh']/1000:.1f} MWh of storage,
{energy['connected_charging_power_kw']/1000:.1f} MW of connected charging and
{energy_plan.solar_plant_kw/1000:.1f} MW of dedicated solar. Operating energy,
islanding, connections, protection, land and duty remain unaccepted.

City planning CAPEX is USD {capex/1e9:.2f} billion before owner-confirmed land,
utilities, tax/duty and escalation. The {money(buckets['depots'])} depot allowance
is **not reconciled** to surveyed stabling, workshops, energy, fire and security.
The Baghdad manufacturing plant is outside city CAPEX and counted once in the Baghdad-only programme.

## Iraq financing proposal

The [city funding model](../engineering/finance/FUNDING-MODEL.md) and
[Baghdad-only programme](../../IRAQ-FUNDING-PROGRAMME.md) divide eligible Chinese
component invoices, government capital, IQD bonds and IQD bank credit.
Government capital is 25% of total CAPEX, including **USD {programme['government_capital_usd_cash']/1e6:,.2f} million**
for half the imported-parts budget. Proposed Chinese USD credit covers the other
half. Remaining government capital, bonds and bank credit are in IQD. Full import
basket lender and supplier-origin qualification remains pending. Fees, interest, reserves and
cash support beyond that contribution are separately disclosed funding needs.
They include staged draws, native-currency principal/interest, fees, reserves,
cash support and downside funding gaps. The rates, maturities and 50% invoice
advance are uncommitted appraisal assumptions. The resource-constrained
construction cash schedule is not a five-year funding promise. Monthly and
annual ledgers and charts are generated from the same controlled model.

The programme comparison covers the historical 148 km / USD 18 billion proposal
against this {comparison['osr_route_km']:,.1f} km / {comparison['osr_stations']} station planning network.
Total USD capital funding (government USD cash plus Chinese loan) is
USD {programme['usd_denominated_capital_usd']/1e9:.3f} billion; the rest is IQD.
The older all-USD financing basis is the requested comparison scenario, not
verified final contract terms. The modelled fare is IQD {comparison['fare_iqd']:,.0f}
per paid trip. Population access uses a {comparison['anchor_weighted_coverage']:.1%}
anchor-weighted planning score, not a surveyed resident catchment. Local
procurement is USD {comparison['osr_local_purchases_usd']/1e9:.3f} billion equivalent;
indicative operating employment is {comparison['operating_fte']:,} FTE. Construction
job counts require validated hours and productivity. The model leaves USD
{programme['additional_funding_required_with_25_percent_cap_usd']/1e9:.3f} billion in additional
cash requirements in the full-network-only case if public funding is capped at the
25% capital contribution. The conditional phased case reduces this to USD
{programme['phased_opening']['cases']['low_demand']['additional_funding_required_usd']/1e9:.3f} billion,
with first / last line openings in months
{programme['phased_opening']['cases']['low_demand']['metrics']['operations_start_month']} /
{programme['phased_opening']['cases']['low_demand']['metrics']['full_network_operations_start_month']}.
These are gross nominal liquidity needs, not net lifetime loss. Opening dates
require actual plant, depot, line and safety acceptance; fleet-based phase demand
and the 25% fixed / 75% variable OPEX split remain planning assumptions.

The [independent reconciliation](../engineering/finance/FUNDING-RECONCILIATION.md)
and [six-month bond and loan requirements](../../finance/baghdad-unfunded_reference-six-month-tranches.csv)
separate capital from debt repayment and price additional liquidity.
Pooling city/plant cash yields USD {reconciliation['gross_additional_liquidity_usd']/1e9:.3f} billion
gross early cash needs and USD {reconciliation['later_retained_cash_usd']/1e9:.3f} billion
later retained cash: a USD {reconciliation['net_lifetime_liquidity_gap_usd']/1e6:.2f} million
net nominal deficit before gap-finance interest and fees. The illustrative
green/concessional/grant/development mix still leaves USD
{independent['cases']['blended_candidate']['terminal_supplemental_balance_iqd']/fx/1e9:.3f} billion
equivalent unpaid gap debt with constant nominal fares and OPEX. It is not a funded programme.
Steady annual tickets, shop/kiosk leases and advertising already contribute IQD
{receipts['farebox_annual_usd']*fx/1e9:.1f}, {receipts['station_retail_annual_usd']*fx/1e9:.1f}
and {receipts['station_advertising_annual_usd']*fx/1e9:.1f} billion respectively;
new revenue targets cannot count those receipts again.

The separate paired sensitivity increases fares and OPEX 5% annually from
financial close. With 5% income growth and the other blended assumptions,
peak supplemental debt is IQD {indexed['peak_supplemental_balance_iqd']/1e12:.3f} trillion,
with no terminal unpaid facility. Average nominal tickets reach IQD
{indexed_prices['first_opening']['average_paid_fare_iqd']:,.0f} at first opening and IQD
{indexed_prices['full_opening']['average_paid_fare_iqd']:,.0f} at full opening; commuting
uses {indexed_prices['full_opening']['forty_four_trips_income_share']:.1%} of the indexed income proxy.
This conditional sensitivity does not demonstrate household income growth or
placed lending. Separate cases test peak/off-peak tickets, slower income growth
and higher OPEX inflation. Capital escalation and future FX changes remain open.
The [paired 5% six-month schedule](../../finance/baghdad-fare_5pct_opex_5pct-six-month-tranches.csv)
and [monthly prices](../../finance/baghdad-fare_5pct_opex_5pct-monthly-prices.csv)
show those cashflows and affordability assumptions.

"""
    text, count = re.subn(r"## Proposed system\n.*?(?=## Rolling stock)", system, text, flags=re.S)
    if count != 1:
        raise ValueError("offer README needs one controlled proposed-system section")
    text, count = re.subn(r"The Baghdad package already instantiates.*?These feed the project twin, operations portal,", f"The Baghdad package already instantiates {ops_totals['assets']:,} assets, {ops_totals['manufacturing_tasks']:,} manufacturing and verification tasks, {ops_totals['manufacturing_materials']:,} material/procurement rows, {ops_totals['maintenance_tasks']:,} maintenance tasks and {ops_totals['qa_actions']:,} QA actions. These feed the project twin, operations portal,", text, flags=re.S)
    if count != 1:
        raise ValueError("offer README needs one controlled operations summary")
    offer_readme.write_text(text)

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
        Table([[p(f"{lines} lines", "CoverCard"), p(f"{stations} stations", "CoverCard"), p(f"{length_km:.1f} km", "CoverCard"), p(f"{fleet} trainsets", "CoverCard")]], colWidths=[43.5 * mm] * 4,
              style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#173F4D")),
                                ("BOX", (0, 0), (-1, -1), 0.5, TEAL),
                                ("INNERGRID", (0, 0), (-1, -1), 0.5, TEAL),
                                ("TOPPADDING", (0, 0), (-1, -1), 7),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 7)])),
        Spacer(1, 6 * mm),
        p("Prepared from source-locked open geospatial data, a deterministic city design, native railway simulation, independent SUMO timetable validation and a city-specific project/operations twin.", "OfferSub"),
        p(f"STATUS · PLANNING BASELINE — NOT CONSTRUCTION RELEASE · {TODAY:%d %B %Y}", "OfferSub"),
        PageBreak(),
    ])

    story += section("The proposition", "Executive summary")
    story += [
        p("OpenSourceRail offers Baghdad an owner-controlled way to move from city data to a buildable railway programme: route planning, topography and water screening, civil classification, fleet and energy sizing, timetable simulation, manufacturing/procurement planning, maintenance, ERP/HR workflows, SCADA boundaries and certification evidence all share one configuration baseline."),
        cards([
            (f"{length_km:.1f} km", "double-track route"),
            ("3 min", "peak headway"),
            (f"{finance['revenue_basis']['practical_capacity_passenger_trips_per_day']/1e6:.2f} M", "practical trips/day"),
            (money(capex), "planning CAPEX"),
        ]),
        Spacer(1, 4 * mm),
        callout("Decision requested: authorize a time-boxed owner-led data validation and FEED phase—not construction—then select one priority corridor and a surveyed depot/stabling solution.", TEAL),
        Spacer(1, 4 * mm),
        p("What Baghdad receives", "H2x"),
    ]
    story += bullet([
        f"A reproducible {lines}-line network baseline with {stations} stations, {interchanges} interchanges and open GIS layers.",
        f"A complete planning twin linking {ops_totals['assets']:,} assets to budget, procurement, QA, maintenance and operating records.",
        "A six-car battery-electric fleet concept with candidate CRRC components under competitive procurement.",
        "Deterministic simulation and standards/FMEA evidence that reruns when controlled design inputs change.",
        "A staged assurance route that prevents a planning model from being misrepresented as regulatory approval.",
    ])
    story += [
        p("What this document does not claim", "H2x"),
        p("It is not a bid from CRRC or any other manufacturer; not a demand forecast, land approval, utility agreement, geotechnical design, issued-for-construction package, safety certificate or financing commitment. Values remain planning screens until the named release gates close."),
        fitted_image(CITY / "engineering/screenshots/baghdad-qgis-engineering-map.png", 174 * mm, 78 * mm),
        p(f"City-specific QGIS/GDAL package: {lines} corridors, {stations} stations, {interchanges} interchanges and {len(design['civil_segments']):,} classified civil segments.", "Smallx"),
        PageBreak(),
    ]

    story += section("Network, terrain and civil concept", "Physical system")
    story += [
        cards([
            (f"{civil_lengths['at-grade']/1000:.1f} km", "at grade"),
            (f"{civil_lengths['elevated']/1000:.1f} km", "elevated/viaduct"),
            (f"{civil_lengths['bridge']/1000:.1f} km", "bridge screen"),
            (str(len(design['junctions'])), "junction upgrades"),
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
        p(f"The plan includes {stations} unique stations and {interchanges} interchange complexes. Stations remain prohibited on mapped-water footprints in the automatic planner. Platform, access, evacuation, universal access, fire/life safety, utilities, traffic management and property interfaces require site-by-site G1 design evidence."),
        p("Depot and stabling status", "H2x"),
        callout(f"OPEN GATE · The design allocates {fleet} trainsets operationally, but physical overnight positions, track-by-track capacity, workshop circulation, power/fire separation, security and morning/evening moves are not yet surveyed. The current {money(buckets['depots'])} depot allowance is not reconciled and must not be treated as a final depot cost.", AMBER),
        Spacer(1, 3 * mm),
        p("Proposed FEED action: compare at least three land-backed depot/distributed-stabling options, freeze an operator-owned fleet deployment plan, then update civil, energy, programme and cost baselines together."),
        PageBreak(),
    ]

    full_run = next(run for run in simulation["runs"] if run["duration_s"] == 90_000)
    story += section("Service, fleet and energy", "Operating concept")
    story += [
        cards([
            ("05:30–02:00", "operating day"),
            (str(peak), "peak revenue fleet"),
            (f"{spares} + {reserve}", "spare + cold reserve"),
            (f"{energy_plan.scheduled_daily_train_journeys:,.0f}", "one-way trips/day"),
        ]),
        Spacer(1, 3 * mm),
        p(f"The full native run covers 90,000 seconds and {full_run['train_km']:,.0f} train-km with zero invariant violations. Eight degraded cases—including aged batteries, maximum HVAC load, charging-contact loss, grid outage, missed charges and charger conflict—pass the present software model. SUMO independently records {arrived}/{scheduled} planned validation services arriving."),
        fitted_image(CITY / "engineering/screenshots/baghdad-simulation-dashboard.png", 174 * mm, 74 * mm),
        p("Native two-hour evidence trace; the full service-day-plus-run-out and degraded cases are retained as hashed JSON evidence.", "Smallx"),
        data_table([
            ["Energy element", "Planning baseline", "Release boundary"],
            ["Traction demand", f"{energy_plan.annual_energy_kwh/1e6:,.1f} GWh/year", "Calibrated vehicle/duty data and operator timetable"],
            ["Station/depot PV", f"{energy['pv_nameplate_kw']/1000:.1f} MW", "Surveyed roofs/sites, yield, structure, protection"],
            ["Stationary storage", f"{energy['storage_capacity_kwh']/1000:.0f} MWh", "Supplier product, fire strategy, degradation and duty"],
            ["Connected charging", f"{energy['connected_charging_power_kw']/1000:.0f} MW", "Grid/interface studies, selectivity and timetable conflicts"],
            ["Dedicated solar", f"{energy_plan.solar_plant_kw/1000:,.1f} MW", "Land, connection, PPA/ownership and measured resource"],
        ], [40 * mm, 43 * mm, 91 * mm]),
        Spacer(1, 2 * mm),
        callout("The model's zero residual grid/PPA import is a planning result. It is not proof of islanded operability or an approved grid connection; operating energy is explicitly marked unvalidated.", AMBER),
        PageBreak(),
    ]

    story += section("Rolling stock with a candidate CRRC parts package", "Industrial system")
    story += [
        p(f"The proposed fleet is {fleet} OpenSourceRail six-car battery-electric trainsets. The vehicle architecture, requirements, interfaces, FMEA, maintenance identities and acceptance gates remain owner-controlled. CRRC product families are included as candidate components because CRRC publicly lists traction and electrical control equipment and vehicle components—not because a supplier has been appointed."),
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
            (f"{capital['local_percentage_of_total']:.1%}", "modelled local capital"),
        ]),
        Spacer(1, 3 * mm),
        data_table([
            ["Planning bucket", "Value", "Critical qualification"],
            ["Civil works", money(buckets['civil']), "Survey/land/utilities/geotechnical and detailed structures"],
            ["Stations", money(buckets['stations']), "Site fit, passenger/fire/accessibility and MEP design"],
            ["Rolling stock", money(buckets['rolling_stock']), "Competitive supplier offer, qualification and support"],
            ["Solar plant", money(buckets['solar_plant']), "Land, grid, measured resource and commercial structure"],
            ["Depots", money(buckets['depots']), "Not reconciled; replace after depot/stabling FEED"],
            ["Other systems / EPC", money(sum(buckets[k] for k in ('signalling', 'charging_microgrid', 'epc_overhead'))), "Control, charging, project services and integration"],
        ], [49 * mm, 32 * mm, 93 * mm]),
        Spacer(1, 3 * mm),
        fitted_image(OFFER / "screenshots/baghdad-project-twin.png", 174 * mm, 71 * mm),
        p(f"Baghdad project twin: {project['totals']['programme_working_days']:,} planning days, {project['totals']['critical_work_packages']:,} critical work packages and {project['totals']['pre_ntp_order_actions']:,} pre-NTP actions. Its status is explicitly “planning-digital-twin-not-construction-release”.", "Smallx"),
        p("The foreign-turnkey and localisation figures are sensitivities, not received bids. Land, taxes/duties, utility relocation, escalation and unresolved depot scope must be owner-defined before affordability decisions. Financing fees are separately modelled in the Iraq cashflow."),
        PageBreak(),
    ]
    story += section("Iraq sources, repayments and public cash", "Structured financing appraisal")
    metrics = funding["base"]["metrics"]
    native_city_sources = []
    for key, value in metrics["capital_sources_usd"].items():
        if key == "government":
            native_city_sources += [["Government import cash", "USD", money(metrics["government_capital_usd_cash"])], ["Government local cash", "IQD", f"IQD {metrics['government_capital_iqd_cash']/1e12:.3f} trillion"]]
        elif key == "chinese_export_credit":
            native_city_sources.append(["Chinese loan", "USD", money(value)])
        else:
            native_city_sources.append([key.replace("_", " "), "IQD", f"IQD {value*funding['assumptions']['model']['iqd_per_usd']/1e12:.3f} trillion"])
    story += [data_table([["City capital source", "Currency", "Proposed native amount"], *native_city_sources], [80*mm, 24*mm, 70*mm]), Spacer(1, 3*mm),
        fitted_image(CITY / "engineering/finance/funding-cashflows.png", 174*mm, 108*mm),
        p(f"Construction cash spans {metrics['construction_cash_months']} assumed calendar months under the current constrained CPM. Peak annual conditional public cash requirement is {money(metrics['peak_annual_government_cash_usd'])}; loan repayment is tied to draw dates, not postponed until opening.", "Smallx"),
        p("The import basket is assumed eligible for proposed Chinese export credit pending supplier-origin and lender qualification. Imported purchases are split 50% government USD cash / 50% Chinese USD loan. Government capital is 25% of total uses, including invoice downpayments. Proposed IQD bonds and term bank credit split the remaining balance after government and Chinese credit 75:25. Tooling is counted once in the Baghdad-only programme outside city CAPEX. Fees, interest, reserves and later cash shortfalls remain additional unfunded requirements if public cash is limited to that contribution. Loan advance, rates, maturities and origination fees are uncommitted assumptions, not bank offers."),
        p("Monthly ledgers separately show native-currency draws, principal, interest, fees, fare/nonfare receipts, OPEX, public support and restricted reserves. FX, demand, delay, short-bullet bonds, withheld appropriations and declined Chinese credit are stressed. Subsidy does not increase pre-support DSCR; no automatic refinancing or unlimited bridge credit is assumed."), PageBreak()]

    story += section("Baghdad: USD capital intensity and local industrial value", "Historical proposal comparison")
    story += [
        fitted_image(CITY.parent / "finance/baghdad-financing-comparison.png", 174*mm, 78*mm),
        data_table([
            ["Measure", "OSR plan including plant", "Historical / requested scenario"],
            ["Route / stations", f"{comparison['osr_route_km']:.1f} km / {comparison['osr_stations']}", "148 km / 64"],
            ["Capital USD equivalent", money(programme['total_capex_usd']), "$18 billion reported"],
            ["USD capital funding", money(programme['usd_denominated_capital_usd']), "$18 billion assumed USD"],
            ["Chinese USD loan", money(programme['usd_denominated_debt_principal_usd']), "Debt/government split unknown"],
            ["Government import USD cash", money(programme['government_capital_usd_cash']), "Unknown final split"],
            ["Remaining funding", f"IQD {(programme['total_capex_usd']-programme['usd_denominated_capital_usd'])*funding['assumptions']['model']['iqd_per_usd']/1e12:.3f} trillion", "No IQD in requested scenario"],
        ], [57*mm, 57*mm, 60*mm]),
        p('Sources: <link href="' + comparison["third_party"]["source_report"] + '">July 2024 report</link>; <link href="' + comparison["third_party"]["source_nic"] + '">NIC DBOMFT notice</link>.', "Smallx"),
        p("The July 2024 report gives 148 km, seven lines, 64 stations and an estimated $18 billion. The NIC DBOMFT notice requires a bidder funding plan. Entirely USD foreign loans and government cash are the requested comparison assumption; contracted currency, fares and debt terms have not been verified. Historical and OSR planning budgets differ in scope, price date and maturity; this is not a qualified bid saving.", "Smallx"),
        p(f"Only the Chinese loan is USD debt. Half the imports are government USD cash inside its 25% capital contribution. Remaining government cash, bonds, bank credit and local revenue use IQD. Imported-purchase FX exposure is {money(comparison['osr_imported_purchases_usd'])}; IQD debt matching reduces currency mismatch but does not remove Chinese repayment FX risk or domestic interest and placement needs.", "Smallx"), PageBreak(),
    ]
    story += section("Affordable service and direct Iraqi benefits", "Sustainability appraisal")
    story += [
        p(f"Modelled average fare: IQD {comparison['fare_iqd']:,.0f} per paid trip. Thirty trips use 8% of the retained income proxy; 44 commuter trips use 11.7%. The low case assumes {comparison['annual_low_case_paid_trips']/365:,.0f} paid trips/day, not unique residents or calibrated demand. At that volume, OPEX-only neutrality requires IQD {comparison['operating_only_neutral_fare_iqd_at_low_trips']:,.0f}; this excludes debt and reserves."),
        p(f"First complete operating year cash neutrality including debt and fees requires about IQD {comparison['first_operating_year_neutral_fare_iqd_including_debt_and_fees']:,.0f} per trip at fixed ramped demand, excluding factory debt and reserve deposits. This is a threshold, not a recommended fare. The full-network-only case with {metrics['construction_cash_months']} capital months leaves {money(programme['additional_funding_required_with_25_percent_cap_usd'])} in unfunded additional cash requirements under the public cap; higher fares alone cannot finance that construction-period burden."),
        p(f"Conditional phased opening starts line revenue in month {programme['phased_opening']['cases']['low_demand']['metrics']['operations_start_month']} and reaches all lines in month {programme['phased_opening']['cases']['low_demand']['metrics']['full_network_operations_start_month']}. Programme additional liquidity needs fall to {money(programme['phased_opening']['cases']['low_demand']['additional_funding_required_usd'])}. Each line has its own revenue ramp; fleet shares proxy demand and variable OPEX, with 25% fixed OPEX from first opening. The new plant gates train production for 520 working days. Actual commissioning remains pending. Later surplus is retained: these gross cash injections are not net lifetime loss.", "Smallx"),
        p(f"Population access is unresolved: the {comparison['anchor_weighted_coverage']:.1%} anchor score applied to {comparison['planning_population']:,} planning residents yields a {comparison['anchor_based_resident_proxy']:,} resident proxy. It is not a measured 800 m walking catchment. The older reported 80% city-coverage ambition has no comparable access definition. More route kilometres and stations do not prove greater population coverage."),
        p(f"Potential Iraqi procurement is {money(comparison['osr_local_purchases_usd'])}, covering civil works, stations, train assembly, body modules, fit-out, wiring, inspection and maintenance. Imported bogies, batteries, windows, doors and tooling still need qualification. Local production can retain skills, supplier income and repair capacity; no GDP multiplier or tax recovery is booked."),
        p(f"The operating allowance is {comparison['operating_fte']:,} indicative FTE and IQD {comparison['operating_labour_annual_iqd']/1e9:.2f} billion annual labour cost. These are not manufacturing/construction job counts; validated hours, productivity, wages and local-content contracts are required. The third-party plan may also employ Iraqi civil labour."),
        p("Sustainability requires accepted phasing, surveyed demand, an affordable tariff, funded interest/reserves and debt service within the public limit, placed IQD facilities, local supplier/process qualification and lifecycle replacement provision. Software and ledger checks do not close these decisions."), PageBreak(),
    ]
    story += section("Reconciled cash needs and financing alternatives", "Six-month funding programme")
    story += [
        p(f"Capital sources and uses remain {money(reconciliation['capital_uses_usd'])}. Independent pooled cash requires {money(reconciliation['gross_additional_liquidity_usd'])} early and retains {money(reconciliation['later_retained_cash_usd'])} later: {money(reconciliation['net_lifetime_liquidity_gap_usd'])} net nominal deficit before charging for gap finance. EPC overhead now follows direct works; capital principal repayments are not extra construction CAPEX."),
        data_table([['Existing annual receipts', 'IQD billion, full steady operation'],
               ['Passenger tickets', f"{receipts['farebox_annual_usd']*fx/1e9:.3f}"],
               ['Station shops / kiosk leases', f"{receipts['station_retail_annual_usd']*fx/1e9:.3f}"],
               ['Advertising space', f"{receipts['station_advertising_annual_usd']*fx/1e9:.3f}"]], [95*mm, 79*mm]),
        p("These receipts already reduce the gap. Retail assumes 88% occupancy and advertising 85%; rates follow the historical income proxy. Each line's receipts ramp with opening. Tenant demand, collection losses and dedicated concession costs remain unqualified; new income must be additional and net of costs.", "Smallx"),
        p("Six-month placement envelopes specify native government cash, Chinese loan draws, IQD bond face and unit counts, IQD bank draws, first/last repayment dates, reserve movements and supplemental liquidity. Settlement is monthly against expenditure at par; selling each entire envelope upfront would need a new interest/carry calculation."),
        data_table([['Gap-finance sensitivity', 'Peak IQD tn', 'Uncovered IQD tn', 'Unpaid at end IQD tn']] + [
            [name.replace('_', ' '), f"{independent['cases'][name]['peak_supplemental_balance_iqd']/1e12:.3f}",
             f"{independent['cases'][name]['uncovered_support_iqd']/1e12:.3f}",
             f"{independent['cases'][name]['terminal_supplemental_balance_iqd']/1e12:.3f}"]
            for name in ('commercial_gap_credit', 'concessional_gap_credit', 'blended_candidate')], [73*mm, 30*mm, 35*mm, 36*mm]),
        p("The illustrative IQD facility has a 13 trillion maximum outstanding balance and pays its own interest/fees. The candidate combines eligible green debt replacing conventional bonds, an uncommitted climate grant, net development-rights proceeds and new net receipts. None is a funding commitment; a green label alone changes no cashflow.", "Smallx"),
        p(f"With constant nominal fares and OPEX, eliminating both uncovered cash and terminal debt requires about {money(independent['additional_receipts_threshold']['incremental_net_receipts_annual_usd'])}/year of genuinely new net receipts under the other blended assumptions. Indexed fares and costs are tested separately on the next page. IQD on-lending or a priced hedge is needed for foreign concessional funding to preserve the currency strategy.", "Smallx"),
        p("Detailed calculations, full six-month CSVs and primary-source financing routes are in engineering/finance/FUNDING-RECONCILIATION.md and the Iraq finance directory."), PageBreak(),
    ]
    story += section("Variable tickets and indexed operating costs", "Fare and inflation sensitivities")
    story += [
        p("A 5% annual ticket increase is tested alongside OPEX inflation, income growth and demand response. Annual indices start at financial close; no receipts enter before opening. Peak/off-peak tiers are indicative, with a separate demand response for each tier. No tariff or inflation forecast is adopted."),
        data_table([['Policy', 'Peak debt IQD tn', 'Uncovered IQD tn', 'End debt IQD tn']] + [
            [label, f"{independent['cases'][name]['peak_supplemental_balance_iqd']/1e12:.3f}",
             f"{independent['cases'][name]['uncovered_support_iqd']/1e12:.3f}",
             f"{independent['cases'][name]['terminal_supplemental_balance_iqd']/1e12:.3f}"]
            for name, label in (('fare_5pct_opex_5pct', 'Fares / OPEX / income +5%'),
                                ('variable_fare_5pct_opex_5pct', 'Peak/off-peak plus 5% indices'),
                                ('fare_5pct_opex_5pct_income_2pct', 'Fares/OPEX +5%; income +2%'),
                                ('fare_5pct_opex_7pct', 'Fares/income +5%; OPEX +7%'))], [78*mm, 30*mm, 33*mm, 33*mm]),
        p(f"In the paired 5% case, first-opening tickets average IQD {indexed_prices['first_opening']['average_paid_fare_iqd']:,.0f}; full-opening tickets average IQD {indexed_prices['full_opening']['average_paid_fare_iqd']:,.0f}. With matched income growth, 44 trips remain {indexed_prices['full_opening']['forty_four_trips_income_share']:.1%} of the income proxy. Slower wage growth raises that burden and reduces trips under the assumed -0.30 real-price elasticity."),
        fitted_image(CITY.parent / 'finance/baghdad-fare-inflation-sensitivities.png', 174*mm, 91*mm),
        p(f"Later surplus repays the illustrative facility under paired 5% assumptions, while substantial early IQD borrowing, the candidate grant/rights receipts and fixed nominal loan terms are still required. The unlevered NPV before grants/new rights/net-receipt targets is {money(indexed['pricing_project_npv_usd_equivalent'])} at {indexed['pricing_nominal_discount_rate']:.1%} nominal discount. Distant nominal surplus is not present-value wealth.", "Smallx"),
        p("Income, occupancy and elasticity are uncalibrated; capital escalation, replacement inflation, FX, variable interest rates and concessional IQD lending need qualification. Affordable commuter/student concessions and transfer caps need explicit compensation rather than assumed free reductions.", "Smallx"), PageBreak(),
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
        Path("cities/catalogue/west-asia/Iraq/Baghdad/engineering/finance/funding-cashflows.png"),
        Path("lib/templates/iraq-funding.toml"),
        Path("lib/templates/baghdad-finance-options.toml"),
        Path("cities/catalogue/west-asia/Iraq/Baghdad/engineering/finance/FUNDING-RECONCILIATION.md"),
        Path("cities/catalogue/west-asia/Iraq/finance/baghdad-finance-reconciliation.json"),
        Path("cities/catalogue/west-asia/Iraq/finance/baghdad-unfunded_reference-six-month-tranches.csv"),
        Path("cities/catalogue/west-asia/Iraq/finance/baghdad-fare_5pct_opex_5pct-six-month-tranches.csv"),
        Path("cities/catalogue/west-asia/Iraq/finance/baghdad-fare_5pct_opex_5pct-monthly-prices.csv"),
        Path("cities/catalogue/west-asia/Iraq/finance/baghdad-fare-inflation-sensitivities.png"),
        Path("cities/catalogue/west-asia/Iraq/finance/baghdad-programme.json"),
        Path("cities/catalogue/west-asia/Iraq/finance/baghdad-financing-comparison.png"),
        Path("cities/catalogue/west-asia/Iraq/IRAQ-FUNDING-PROGRAMME.md"),
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
