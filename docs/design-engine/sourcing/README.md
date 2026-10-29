# Sourcing and cost intelligence — v0.6 research snapshot

**Snapshot date: 29 October 2026.** This dossier connects public material/component evidence and construction benchmarks to the revision-bound v0.6 design twin. It records useful measured catalogue observations and price leads without silently substituting them into the selected vehicle. Every review packet is replayable against its sealed input, source snapshot and implementation.

## What is in the database

The combined offline seed currently contains **60 immutable observations**: 27 source records, 16 product records, five published catalogue offers, two retained FX observations and ten commodity/construction benchmarks. A live refresh against the fixed public ECB and World Bank endpoints retrieved content matching the retained source hashes; it parsed **27 dated ECB reference-rate rows** and **two current World Bank metal observations** into a local append-only database. Repeating the refresh with identical bytes reuses the source record and does not replace previous observations.

Source products are immutable observations. If a supplier product key has multiple recorded revisions, the laminate study stops unless the operator supplies the exact `PRODUCT_KEY=RECORD_ID` selection with `--product-observation`. The requirement and RFQ retain that selected record ID. Material/source-property changes alter the evaluation input and bounds; physical candidate identity stays constant when only the evidence revision changes. A changed material choice or geometry gets a different candidate ID.

The selected raw-material prices are Easy Composites UK catalogue observations in GBP, ex-VAT and dated 29 October 2026: 440 g/m² biaxial cloth, 600 g/m² biaxial cloth, an IP2 resin product, an IN2 resin-plus-hardener kit, and one EC20 vacuum-pump listing. Supplier minimum order quantities and order multiples are not published in the retained snapshot, so the evaluator reports **listed extensions at requested quantities**, while actual order quantities and order totals remain unknown. The EC20 listing's shipping gross mass is kept separate from installed pump mass. The 1 kg IN2 kit price already covers its hardener.

Other retained catalogue evidence includes:

| Evidence | Observation available | Scope still open |
|---|---|---|
| Wabtec ESP4C door mechanism | 46 kg mechanism and hanger assembly | Door leaves, glazing, seals, fixings, controls and complete installed mass; publisher doorway dimensions conflict |
| Thermo King LRV equipment | 560–600 kg product masses and nominal ratings at stated 35 °C test conditions | Baghdad 50–55 °C delivered capacity, HVAC installation, ducts and energy balance |
| LONGi LR7-60HVHL-560M Light Design | 16.3 kg module; 1,990 × 1,134 × 30 mm; 560 W STC | Roof mounting, cabling, protection, fit, local yield and rail vibration/fire evidence |
| ABB ACS880 single-drive family | Industrial-drive family range and advertised ambient/maintenance data | Specific SKU, price, cabinet, cooling, LIM winding compatibility and propulsion duty |
| ArcelorMittal 54E1 rail | 54.77 kg/m profile mass | Grade choice, delivered price, axle-load suitability, fastening and lifecycle |
| Pandrol SD family | Direct concrete-fastening product-family lead | Exact rail/application configuration, spacing and supplier price |
| Elematic E9 | Published casting-speed ceiling for its stated product application | Railway-girder mould/process transfer, bed/cure/crew/QA throughput and cost |
| Liebherr LTM 1100-5.3 | Published capacity at a specific 3 m radius | Actual beam hook load, radius, boom/outrigger configuration and load chart; maximum headline tonnage is not used |
| SKF and Knorr-Bremse | Railway axlebox/bearing and braking system technical source leads | Exact wheelset/brake configuration, compatible products, mass and supplier quotation |
| Gurit Corecell M80 | 85 kg/m³ nominal grade, 81–89 kg/m³ stated range, 3–53 mm sheet thickness range and 1,220 × 2,440 mm sheet format | Marine sandwich-core comparator only; no railway allowables, installed panel definition or public price |

The ABB entry is a **family comparator without a price or compatible part number**. It is not an admitted station-LIM drive. SKF and Knorr-Bremse are registered research sources, not selected components. No product specification or unit cost is inferred from a source URL alone.

## Market and construction sources

The [World Bank Pink Sheet](https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/world-bank-commodities-price-data-the-pink-sheet) October 2026 workbook reports September 2026 aluminium at **USD 3,283/metric tonne** and copper at **USD 14,474/metric tonne**. These are primary-commodity benchmarks, not extrusions, windings, delivered metal or station-motor prices. The public [LME Official Prices page](https://www.lme.com/en/market-data/reports-and-data/lme-official-prices) is registered as a lead; its data-access and redistribution terms are not yet reviewed for automated ingestion, so its displayed prices are not loaded as cost evidence.

Gurit’s [Corecell M page](https://www.gurit.com/corecell-m/) identifies the M80 nominal density and sheet range; its [DNV certificate](https://www.gurit.com/wp-content/uploads/2026/04/CORECELL-M-DNV-1.pdf) is tied to its stated sandwich-core application and is not rail vehicle approval. The two sandwich material screens use that identified product at the declared 20 mm thickness and 85 kg/m³ nominal density. For the 10 m² comparison, the published 81–89 kg/m³ range gives a material-only interval of 40.2–41.8 kg or 36.2–37.8 kg. They do not claim the finished panel uses this core, meets rail fire/smoke or hot-wet limits, or is structurally qualified. No Gurit offer is present, so the study's listed price extensions cover only sourced cloth and resin lines. The manufacturer’s 1,220 × 2,440 mm sheet size is carried into the RFQ draft; the number of sheets remains unknown without panel nesting and a cut plan.

The [ECB daily reference feed](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.pl.html) supplies a dated 28 October snapshot, including EUR/USD 1.1133 and EUR/GBP 0.83785. These are informational reference rates, not executable procurement conversions. IQD is absent; the evaluator does not insert a remembered fixed peg or mix reference rates with a different provider's cash rates.

Eight actual awarded Caltrans bridge-footing concrete pay items are retained in USD/CY, with original bid rates separate from the agency's adjusted rates. They are California historical comparators, **not Baghdad installed rates**. The [Iraq Tender Portal](https://itp.iq/) returned a public application shell without verified award prices. A relevant [UNGM Iraq/UNOPS notice](https://www.ungm.org/Public/Notice/221058) exposed BOQ-file leads, but the file request returned HTTP 403; the importer creates no unit-rate benchmark from those filenames. Local Iraqi concrete, steel, labour, transport, lifting, utility relocation and installation rates remain a high-priority RFQ/tender task.

DigiKey's [official Product Information API](https://developer.digikey.com/tutorials-and-resources/oauth-20-2-legged-flow) supports an explicit future catalogue adapter; production pricing requires a registered organization and credentials. No credentials were present during this run, and no price was fabricated. Quotation file parsers likewise produce unverified claims rather than authenticated Class A offers.

## Direct twin runs

All five packets below passed `./osr source verify` **semantic replay**, including a reconstruction of the historical catalogue and execution of the exact saved request. The database file and downloaded public raw files remain outside the repository. Only the normalized, source-linked packet records are committed here.

| Input and purpose | Evaluation | Result |
|---|---|---|
| Full frame-refinement vehicle registry | 3,183 requirement groups; 40,488 physical occurrences; 15 product observations | 0 compatible supplier matches, 0 priced groups, nine disabled RFQ drafts; no complete vehicle or installed cost |
| Federated whole-railway BOM | 31,989 requirement groups; balanced budget evaluated 137 across propulsion, civil, body, running gear, HVAC, doors, auxiliary power, station and other | 31,852 remain pending; 0 priced groups; 44 selected groups have unknown quantity; nine disabled RFQ drafts |
| 10 m² solid GFRP material hypothesis | 4 × 600 g/m² plies, 50% dry-glass fraction, 10% material scrap | 48 kg conditional material screen; GBP 726.65 published extension across cloth and resin lines; no order total |
| 10 m² sandwich GFRP material hypothesis | 2 × 600 g/m² plies plus declared 20 mm Gurit Corecell M80 grade at 85 kg/m³ nominal; 50% dry-glass fraction; 10% scrap | 41 kg nominal; 40.2–41.8 kg bound over the published core-density range; GBP 363.32 listed extension on priced lines; no core price |
| 10 m² higher-fibre sandwich hypothesis | Same named M80 core; two plies; 60% dry-glass fraction; 10% scrap | 37 kg nominal; 36.2–37.8 kg bound over the published core-density range; GBP 265.55 listed extension on priced lines; no core price |

The laminate rows are **new physical research proposals with ancestry to the federated candidate**. Their 10 m² basis is not measured roof CAD area; the core density, fibre fraction and scrap rate are explicit hypotheses. Resin and cloth prices cover only catalogue raw materials. Adhesive, inserts, consumables, labour, mould/tooling, inspection, transport, installation, fire/smoke, hot-wet performance and structural allowables remain unresolved. These figures cannot rank finished vehicle designs or establish a lower-cost railway.

## Reproducible packages

- [Vehicle registry run](packets/frame-vehicle/summary.json) · [closed packet manifest](packets/frame-vehicle/manifest.json)
- [Whole-railway frontier](packets/federated-balanced-frontier/summary.json) · [closed packet manifest](packets/federated-balanced-frontier/manifest.json)
- [Solid laminate packet](packets/laminate-solid-600gsm/summary.json)
- [Sandwich laminate packet](packets/laminate-sandwich-600gsm/summary.json)
- [Higher-fibre laminate packet](packets/laminate-higher-fibre-sandwich-600gsm/summary.json)
- [Machine-readable run index](validation.json)

From a repository checkout:

```bash
./osr source init
./osr source seed
./osr source refresh
./osr source run \
  --input docs/design-engine/frame-refinement/packet \
  --as-of 2026-10-29 --target-currency GBP \
  --output /tmp/osr-frame-sourcing-review
./osr source verify /tmp/osr-frame-sourcing-review
./osr source study laminate \
  --input docs/design-engine/digital-twin/3a07936303fe5d471a88c95875e55b73b13a5cda94e98d1169f168c647766a93.tar.gz \
  --member federated-bom.json.gz --as-of 2026-10-29 --target-currency GBP \
  --output /tmp/osr-laminate-studies
./osr source verify /tmp/osr-laminate-studies/solid-600gsm
./osr source serve
```

The SQLite database defaults to the user's XDG state directory, outside the checkout. Raw feed bytes default to the user's XDG data directory; the scheduled CI job retains only JSON status artifacts, not feed files or credentials. The Workbench binds to `127.0.0.1:8774`, uses paginated projections and denies every HTTP write method. RFQ drafts remain disabled; no supplier is contacted and no ERPNext production record or active manufacturing order is changed.

## Remaining closure work

The next high-value data is exact source-bound product mappings and supplier RFQs for the actual station-LIM winding/converter, complete passive bogie, independent brake, HVAC at Baghdad design temperature, doors/glazing, and precast guideway/foundation assemblies. The source database can retain the evidence, produce a draft request package, and invalidate dependent evaluations when an approved proposal changes. It cannot make missing geometry, source documents, supplier replies, Iraqi installed rates or physical test data appear. The whole-cell run has **zero exact priced matches**, and complete installed/whole-life cost, physical qualification and an integrated selected railway remain `unknown`.
