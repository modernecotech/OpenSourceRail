# OpenSourceRail for railway operators

For the corrected 17.46 km Airport study, compare both supply enquiries against the audit of service, outages, civil works and prices. The earlier 12 km prototype twin remains available for inspecting car and structure drawings and reproducing its departure and outage cases. [Six-site paired enquiry](../../cities/Baghdad/engineering/simulation/audited-enquiry.zip) · [30-site radial enquiry](../../cities/Baghdad/engineering/simulation/audited-enquiry-radial30.zip) · [Corrected Airport audit](../../cities/Baghdad/engineering/simulation/AUDIT-RESULTS.md) · [Historical prototype twin](../../cities/Baghdad/engineering/prototype/review.html)

[Download the illustrated operator briefing (PDF)](OpenSourceRail-Operator-Brief.pdf) · [Download the offline workshop kit](https://raw.githubusercontent.com/modernecotech/OpenSourceRail/main/docs/operator-review/OpenSourceRail-Operator-Kit.zip) · [Open the delivery workplan](WORKPLAN.md) · [Read the Baghdad proposal](../../cities/Baghdad/PROPOSAL.md)

Use this pack to review the railway with an operations director, chief engineer, financing team and local builders. The core example is a 30 km elevated railway with a six-car, 276-place train and overhead power. Baghdad’s seven corridors and independent citywide option use 700-place trains and protected conductor rail. Each has its own construction, service and funding assumptions. The digital designs support layout review, costing and prototype quotations. Site surveys, supplier terms, physical tests and operating authorisations remain open.

For a discussion of the 605 km concept, start with the central coverage map. It distinguishes operating, deferred and reserved sections and compares walks to stops with a new two-trunk study. [Central Baghdad access review](../../cities/Baghdad/CENTRAL-ACCESS.md)

## Run a 30-minute operator review

For a presentation, open the PDF. In the running Workbench, the **Operator review** navigation opens the models, funding, staffing and control-room views. For an interactive meeting without an installation, extract the workshop ZIP and open **START.html**. The kit includes both models, the Baghdad proposal, maps, factory plans and the calculators. In a repository checkout you can also open the local HTML files below. The timetable card, twins, equipment replay, funding calculator and workforce planner run offline. GitHub's file view displays their source. The PDF and PNGs can be viewed directly on GitHub.

| Time | Open | Operator task |
|---|---|---|
| 0–5 min | [Baghdad map and locations](../../cities/Baghdad/maps/README.md) | Open the [timetable card](../../cities/Baghdad/service-diagrams.html) to follow one set through a terminal turn. Trace the airport corridor on the original NIC map, then use the separate place-name review to identify missing locations. Compare the airport entrance and interchange assumptions against local knowledge. |
| 5–12 min | [Train and station twin](twins/index.html) · [core IFC](twins/core.ifc) · [Baghdad IFC](twins/baghdad.ifc) | Switch between the two designs. Orbit the bogie, select a door, then inspect the platform, viaduct and control equipment. Read the engineering source for each part. Use IFC4 in your own model viewer. |
| 12–16 min | [Control-room replay](screens/supervision.html) · [operating screens](screens/README.md) | Compare a stale section indication with the last observed state. Identify who can authorise isolation or movement, and trace a workshop repair to a serial record. |
| 16–21 min | [Funding and fares](finance/index.html) · [supplier enquiries](finance/purchasing.html) | For the seven corridors, compare 50% borrowing over 20 years at 4% real with 12 years at 7%. Enter paid journeys and net fare receipts. Ask vendors for matched cash prices, debt terms and Iraqi value added. |
| 21–26 min | [Factory layouts and training plan](delivery/README.md) · [Staffing calculator](delivery/index.html) | Follow a car from frame jig to dispatch and a beam from casting bed to site. Identify who signs the hold points. Compare shift coverage, trained staff and yard space with the proposed production rate. |
| 26–30 min | [Workplan and opening decisions](WORKPLAN.md) | Agree an area to survey, a prototype interface to witness, a local package to quote and an owner for each decision. |

![Baghdad station, train and viaduct in the interactive assembly viewer](twins/baghdad-station.png)

The core train workings assign 576 daily trips to 44 sets and show the effect of losing a set or terminal berth. The earlier Airport opening study estimated $813.7m including local works on the 12 km schematic. Use the revised audit for current Airport scope and priced subtotals. [Core train workings](../reference-v07/integration/TIMETABLE.md) · [Historical Airport opening study](../../cities/Baghdad/AIRPORT-OPENING.md) · [Corrected Airport prices](../../cities/Baghdad/engineering/simulation/AUDIT-RESULTS.md)

## Design records for a technical meeting

| Railway package | Core design | Baghdad design |
|---|---|---|
| Body, bogie, braking and replacement | [Powered train](../reference-v07/digital/vehicle/README.md) · [powered brake fixture and separate passive bogie study](../../engineering/interface_studies/REFERENCE-RIGS.md) | [Frame drawing, stock list and removal trials](../../cities/Baghdad/engineering/mechanical/vehicle/README.md) |
| Station, platform, span and foundations | [Joined geometry and interfaces](../reference-v07/integration/README.md) · [selected 13-strand beam](../reference-v07/digital/civil/README.md) | [Station sections, moving-load check and footing trial](../../cities/Baghdad/engineering/mechanical/civil/README.md) |
| Power, electronics and software | [Equipment schedule and software functions](../../control-electronics/README.md) · [vehicle and station software](../../crates/README.md) | [Door, brake and section sequence, wiring, fault tests and repair](../../cities/Baghdad/engineering/controls/README.md) |
| Production, staff and repair | [Parts and manufacturing routes](../reference-v07/manufacturing/README.md) · [production handoff](../reference-v07/digital/production/README.md) | [Delivery and local production quantities](../../cities/Baghdad/COST-AND-DELIVERY.md) · [factory and shift plans](delivery/README.md) |

## Taking drawings to a supplier

Open **Supplier enquiries** in the offline kit. For the Airport, extract the budgetary enquiry and open its README. Give each bidder the issued lot and request scope-matched returns against its ID. For the seven-corridor or core reference, use the separate first-article worksheet to download the relevant design and drawing revisions. The earlier Airport drawings and ERP schedules remain available for historical reproduction. [Supplier enquiries](finance/purchasing.html)

Enter the delivered first-article cash price, documented domestic and imported values, repair terms and evidence reference for each return. The screen identifies untraced value. The buyer confirms both scopes match before the screen compares prices. Save each return locally to resume a meeting. Actual supplier returns belong in the buyer’s confidential records. [Pricing screen](finance/purchasing.html) · [Baghdad negotiation and capital reconciliation](../../cities/Baghdad/BUYER-COMPARISON.md)

![Two hypothetical accessible-station returns showing price, documented Iraqi value and untraced cost](finance/supplier-returns.png)

## What the funding screen shows

The core comparison spreads capital evenly across the 43 construction months as a provisional draw schedule. Full annual operations start in relative Year 5. Renewals are $160m in operating year 15 and $70m in year 25. Baghdad uses the annual project schedules for construction, operating costs and renewal events. Interest on construction draws is paid from the buyer's budget. Changes to a fare scenario affect receipts only. Figures use constant 2026 US dollars. Quotes, exchange rates, fees and public-service agreements will affect a real contract. The seven-corridor screen opens with Iraqi pay and electricity, a posted fare of IQD 750 and 188.4m paid journeys. The central case collects $79.5m and needs $414.1m of public funding including debt service. [Iraq estimate and sources](../../cities/Baghdad/IRAQ-ESTIMATES.md) [Core cost and renewal basis](../reference-v07/cost/README.md) · [Baghdad debt schedules](../../cities/Baghdad/financing-scenarios.json)

![Interactive funding screen for Baghdad’s seven corridors with hypothetical ridership and fare receipts](finance/baghdad-funding.png)

## What to take away from the meeting

| Decision | Record before the meeting closes |
|---|---|
| Where to open | The proposed terminal pair, access to a depot and power, unresolved locations, the busiest expected hour and the owner of the next survey. |
| What to prototype | The railway and drawing revision, the component or interface under review, the measurement needed and who will witness it. Examples include a bogie exchange, a deck edge under load or a stopped train passing from parking hold to dispatch. |
| What to ask a vendor | A cash quotation against the same quantities as its financed offer, imported and domestic content, tooling and software rights, training commitments and a local repair demonstration. |
| How to pay and staff the service | The funding term, paid journeys, net receipt, annual public contribution, duty coverage, relief assumptions and loaded pay used in the scenario. Assign an owner to replace each assumption with evidence. |

For a second session, take the figures to the [finance guide](finance/README.md) and [workforce plan](delivery/README.md). Both explain the units and assumptions needed to reproduce the displayed result. The [workplan](WORKPLAN.md) sets out the owners and evidence needed at the next project decision.

## Opening the workshop on a meeting computer

- **GitHub shows HTML source.** Use the PDF for a slide-by-slide review, or download the ZIP for the working screens. A browser can open the extracted **START.html** directly.
- **A local page has no data or styling.** Extract the complete kit to one directory and reopen its start page. The model data, scripts and styles sit beside the HTML files. Copy the whole directory when moving the demonstration to another computer.
- **A design record opens GitHub.** The kit carries the drawings, models, cost documents and interactive tools used in the workshop. Links to the wider repository need internet access. For an offline site visit, bring local copies of any additional supplier or engineering records you plan to discuss.

## Reproduce the presentation

From the repository root, the following commands compare the finance and staffing inputs with the published results. The screen gallery and twin guides include their own reproduction instructions. The PDF renderer uses ReportLab, CairoSVG, Pillow and the DejaVu fonts.

```sh
python3 docs/operator-review/finance/build.py --check
python3 docs/operator-review/delivery/calculate.py --check
node docs/operator-review/finance/capture.mjs
python3 docs/operator-review/render_brief.py
python3 docs/operator-review/pack.py
python3 docs/operator-review/pack.py --check
```
