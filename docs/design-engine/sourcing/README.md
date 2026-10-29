# Sourcing and cost intelligence — v0.6 research snapshot

**Snapshot date: 29 October 2026.** This dossier connects public material/component evidence and construction benchmarks to the revision-bound v0.6 design twin. It records useful measured catalogue observations and price leads without silently substituting them into the selected vehicle. Every review packet is replayable against its sealed input, source snapshot and implementation.

## What is in the database

The combined offline seed now contains **268 immutable observations**: 47 source records, 16 product records, five published catalogue offers, two retained FX observations and 198 commodity, construction, wage and local-market benchmarks. The retained ECB and World Bank feed snapshot separately parsed **27 dated ECB reference-rate rows** and **two World Bank metal observations** into a local append-only database. Repeating a refresh with identical bytes reuses the source record and does not replace previous observations. Previously published packets remain source-bound to their earlier catalogue epochs.

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

### Iraqi domestic materials, wages and fabrication leads

The source catalogue now includes an official [CSO September 2026 construction-material bulletin](https://mail.cosit.gov.iq/ar/constr-stat/constr-pr) and its [PDF snapshot](https://mail.cosit.gov.iq/documents/buildings/Employees%20wages/2026/%D9%86%D8%B4%D8%B1%D8%A9%20%D8%A7%D8%B3%D8%B9%D8%A7%D8%B1%20%D8%A7%D9%84%D9%85%D9%88%D8%A7%D8%AF%20%D8%A7%D9%84%D8%A7%D9%86%D8%B4%D8%A7%D8%A6%D9%8A%D8%A9%20%D9%84%D8%B4%D9%87%D8%B1%20%D8%A7%D9%8A%D9%84%D9%88%D9%84.pdf). It reports Iraqi-origin market statistics in thousand IQD; the catalogue normalizes those to IQD and retains the printed basis. These are national material observations, not Baghdad installed rates or exact product quotations.

| Domestic input | Normalized observation | Source scope / limit |
|---|---:|---|
| Reinforcing steel | IQD 989,000/t | Iraqi-origin CSO September 2026 statistic; exact grade, diameter and delivery scope unspecified |
| Ordinary cement | IQD 132,000/t | Iraqi-origin CSO September 2026 national statistic; cement class/strength is not specified |
| Reported regional cement market observation | IQD 120,000/t on 8 October 2026 | Kurdistan Region bulk-market report; a regional official's reported statement, not a seller quotation, Baghdad rate or delivered price |
| Resistant cement | IQD 148,000/t | Iraqi-origin CSO September 2026 statistic; product class/strength needs supplier confirmation |
| Red sand / ordinary gravel / crushed gravel | IQD 21,000 / 21,000 / 24,000 per m³ | CSO table observation; source, grading, moisture, haulage and delivered scope open |
| Ordinary brick | IQD 184 each | Normalized from IQD 184,000 per thousand pieces |
| Skilled worker wage | IQD 75,000 per working day; normalized to IQD 9,375/person-hour | [CSO 2025 annual wages by governorate](https://mail.cosit.gov.iq/documents/buildings/Employees%20wages/2025/2025%D9%86%D8%B4%D8%B1%D8%A9%20%D8%A7%D8%B3%D8%B9%D8%A7%D8%B1%20%D8%A7%D9%84%D9%85%D9%88%D8%A7%D8%AF%20%20%D9%88%D8%A7%D8%AC%D9%88%D8%B1%20%D8%A7%D9%84%D8%B9%D8%A7%D9%85%D9%84%D9%8A%D9%86.pdf), Baghdad average; hourly conversion assumes 8 hours/day and excludes employer burden |
| 2025 regional material and wage series | 72 material benchmarks and 90 hourly wage benchmarks for the 15 governorates listed by CSO | [Official 2025 annual bulletin](https://www.cosit.gov.iq/documents/buildings/Employees%20wages/2025/2025%D9%86%D8%B4%D8%B1%D8%A9%20%D8%A7%D8%B3%D8%B9%D8%A7%D8%B1%20%D8%A7%D9%84%D9%85%D9%88%D8%A7%D8%AF%20%20%D9%88%D8%A7%D8%AC%D9%88%D8%B1%20%D8%A7%D9%84%D8%B9%D8%A7%D9%85%D9%84%D9%8A%D9%86%D8%A9.pdf); printed zeros remain unavailable |
| Aluminium profiles and sheet | IQD 4.60–5.50 million/t profiles; IQD 5.10–5.30 million/t sheet observations | [Ur Company posted prices](https://ur.industry.gov.iq/public/prices); alloy/temper, effective date, terms and availability are unstated |
| Rebar market indicator | IQD 931,000/t observed 29 October 2026 | [Hadeed Iraq marketplace](https://hadeediraq.com/) dashboard; not a seller-specific, grade-specific or delivery quotation |

The [CSO statistics page](https://cosit.gov.iq/ar/63-stat-ar/283-2013-02-11-03-37-09) lists monthly 2026 bulletins and annual wage/material reports. The CSO September ordinary-cement figure and the [8 October Kurdistan Region report](https://theinsightinternational.com/kurdistan-cement-steel-prices-rise-iraq-fuel-subsidy-factories-october/) are retained as separate observations because their dates, geographic coverage and evidence bases differ. The article reports a regional official's statement to Kurdistan24 that bulk cement was IQD 120,000/t, up from IQD 80,000/t. Neither figure is a Baghdad supplier quotation or installed rate. They are not averaged or used as a single candidate price; a local grade-specific supplier quotation is still required.

The CSO rebar statistic and the marketplace indicator differ in date and scope. They are retained separately and are not blended into a fabricated quote. The public [Cement Producers Association directory](https://cpai.iq/companies) identifies Iraqi cement producers for RFQ follow-up. More domestic manufacturing leads are [Star Steel Iraq](https://starsteeliraq.com/manufacturing/) and [Alpha Steel](https://alphasteel.iq/) for reinforcing steel; [Dijla Precast](https://dijla-precast.com/production-lines/), [Karbala Precast](https://karbala-company.com/), [Al-Fayha](https://www.al-fayhagroup.net/products/prefabricated-building-products), [Al-Burhan](https://www.alburhangroup.com/concrete-precast-factory.php) and [Al-Kanz](https://alkanz.iq/about-us/) for precast/piles/girders. Their public pages establish supplier leads only. Request exact grades, certificates, capacity allocation, schedule, warranty, transport and binding project quotations before using them in a candidate estimate. The regional [FRP Technology](https://www.frptechnology.com/) lead advertises an Iraq distribution network, but this does not establish Iraqi GFRP feedstock manufacture or local stock.

Additional domestic production leads are now retained as distinct sources:

| Domestic source | Publicly described capability | Current evidence boundary |
|---|---|---|
| [Iraqi Cement State Company](https://icsc.industry.gov.iq/) | Government cement plants and ordinary/resistant cement production plans | Plant availability, certified grade, delivery and current project price remain unconfirmed |
| [State Company for Steel Industries](https://scosi.industry.gov.iq/) | Steel structures, foundry, crane/tower/galvanizing, mechanical workshop and quality-control units | Capability lead only; no railway component scope, current capacity allocation or quotation |
| [Al Anmaa steel plant](https://ahfed.org.iq/factories/alanmaa/) | Foundation page describes a Khor Al-Zubair EAF/continuous-casting plant and reinforcing bar | Its 800,000 t/year figure is a company-reported capacity claim; current output, grade certificates and availability are unverified |
| [Iraq Alhur GRP factory](https://iraqalhur-grp.iq/en/) | Baghdad/Al-Nahrawan GRP pipe manufacture | Pipe capability does not establish passenger-body panel capability or rail structural/fire qualification |
| [Al-Khassaki aluminium factory project](https://akg-eng.net/al-khassaki-factory-for-melting-and-extruding-aluminum-sections/) | Project page describes planned aluminium melting/extrusion of profiles and sheets | The page states 75% progress; commissioning and operating capacity are not established |

These entries help route domestic procurement and fabrication research. They are not available-to-buy records, validated capacity data, certified component designs or prices. In particular, the aluminium project is not counted as operating capacity and the GRP pipe plant is not treated as a source of qualified vehicle-body panels.

### Regional material + labour estimates

The regional price library uses the CSO 2025 Iraqi-origin material rows and daily wage averages for the 15 governorates in the bulletin. The bulletin excludes Kurdistan Region governorates. Missing source-table values are not interpreted as zero: concrete estimates are held for Kirkuk, Wasit and Salah al-Din because at least one required material price is not reported. Annual market averages are not exact supplier quotations, and wage rates are base averages rather than employer-loaded factory charge-out rates.

The reproducible [regional cost packet](domestic-fabrication/regional-estimates-2025/iraq-domestic-cost-reference-2025.json) contains 84 unit-rate scenarios: concrete batching for 12 governorates, rebar cut/bend for all 15, and an aluminium profile assembly screen for Baghdad. Each uses explicit material quantities, labour hours and a 20% uplift on direct materials plus direct labour. The hours are planning scenarios; the uplift is unallocated and is not verified as tax, profit, contingency or overhead.

| Domestic fabrication scenario | Declared input basis | Estimated rate with 20% uplift |
|---|---|---:|
| Baghdad concrete batching, 2 / 4 / 8 skilled h per nominal m³ | 0.35 t ordinary cement + 0.50 m³ red sand + 0.80 m³ crushed gravel; 2025 Baghdad material and wage statistics | IQD 114,720 / 137,220 / 182,220 per nominal m³ |
| Baghdad rebar cutting/bending, 4 / 8 / 16 skilled h per input tonne | 1 t at the 2025 Iraqi-origin Baghdad rebar statistic plus declared labour | IQD 1,296,600 / 1,341,600 / 1,431,600 per tonne |
| Baghdad aluminium-profile assembly, 8 / 16 / 32 skilled h per input tonne | 1 t at the Ur Company non-oxidized profile page observation (2026) plus 2025 Baghdad wage rate | IQD 5,610,000 / 5,700,000 / 5,880,000 per tonne |

The Baghdad concrete scenarios are also applied to the exact research-candidate nominal-volume takeoff, preserving its 81 manufacturing groups and 486 original engineering occurrences. The 2025 material-rate packet estimates IQD **207.05–328.87 million** for the modeled 1,804.81 m³ nominal concrete volume across the 2/4/8-hour cases. That is a recipe-based estimate for a research candidate, not a structural mix, complete precast span, installed civil price or selected-reference cost. It excludes rebar, prestress, moulds, factory utilities, QA, handling, transport, piers, foundations, erection and maintenance. See the [2 h](domestic-fabrication/regional-estimates-2025/baghdad-concrete-takeoff-2h.json), [4 h](domestic-fabrication/regional-estimates-2025/baghdad-concrete-takeoff-4h.json) and [8 h](domestic-fabrication/regional-estimates-2025/baghdad-concrete-takeoff-8h.json) group-mapped packets.

Regenerate the regional unit-rate scenarios and group-mapped Baghdad concrete packets from the exact takeoff with:

```bash
./tools/automation/osr-python -m engineering.sourcing.iraq_cost_scenarios \
  --takeoff docs/design-engine/sourcing/material-takeoff/federated-v06-stock-takeoff.json.gz \
  --output build/iraq-domestic-cost-scenarios
```

### Candidate material takeoff

`./osr source takeoff material` now produces a material-oriented roll-up from the exact federated railway BOM. The [source-bound takeoff](material-takeoff/federated-v06-stock-takeoff.json.gz) retains all 2,269 manufacturing-group identities and all 27,216 located engineering occurrences, while leaving the 4,773 unlocated accounts separate. It derives **4,780.58 t of located gross stock mass** and **1,804.81 m³ of nominal concrete stock geometry** from the candidate bundle. These are modeled stock quantities; they are not weighed installed mass, purchase orders, or complete project quantities.

| Material family | Candidate stock quantity | Sourced price reference | Treatment |
|---|---:|---:|---|
| Station LIM copper conductor | 9.35424 t across five banks | USD 14,474/t; raw commodity extension USD 135,393.27 | World Bank September 2026 copper benchmark; winding conductor, insulation, winding labour, converter, cooling and installation remain unpriced |
| Vehicle-body aluminium reference | 17.53561 t | USD 3,283/t; raw commodity extension USD 57,569.40 | World Bank September 2026 aluminium benchmark; sheet/extrusion mix, alloy, forming, joining, finish and installation remain unpriced |
| Proposed 6082-T6 onboard secondary | 1.65206 t | USD 3,283/t; raw commodity extension USD 5,423.70 | Primary aluminium benchmark only; alloy/temper premium, plate form, machining and assembly remain unpriced |
| Concrete guideway stock | 4,512.02 t; 1,804.81 m³ | Illustrative raw-material + labour scenario: IQD 113,580–181,080 per nominal m³ | No design mix, finished concrete offer, reinforcement/prestress closure, or local installed concrete quote |
| 60E1-equivalent rail | 195.08 t | No compatible rate | The retained ArcelorMittal catalogue observation is for a different rail profile; no price is transferred |

The metal extensions are raw-commodity comparisons, **not accepted supplier matches, product prices, cost bounds or installed-cost estimates**. The takeoff links the Baghdad CSO skilled-worker wage observation of IQD 9,375/person-hour, normalized from the 2025 daily average using an 8-hour day. The 2,269 groups do not declare measured labour hours. A separate recipe applies explicit 2/4/8-hour scenarios only to the concrete roll-up; all other manufacturing groups remain without calculated labour or fabrication costs. The rebar and concrete examples below are material-plus-labour scenarios, and their hours and mix quantities remain planning assumptions.

### Draft procurement-package BOM

The [package packet](procurement-bom/federated-v06-research-packages.json.gz) groups all **27,216 located stock occurrences** in the federated research candidate into 191 hierarchy-based sourcing-package candidates. It preserves each engineering occurrence, manufacturing-group identity, and related procurement/manufacturing task ID. The **4,773 unlocated obligations remain separate** and do not enter package masses or quantities.

| Draft sourcing scope | Packages | Located occurrences | Modeled gross stock mass |
|---|---:|---:|---:|
| Vehicle-body-system stock kit, by car | 6 | 23,466 | 19.21 t |
| Passive-bogie stock package | 12 | 360 | 29.79 t |
| Passive-secondary stock kit, by car | 6 | 312 | 1.65 t |
| Rail stock pair, by span | 81 | 162 | 195.08 t |
| Nominal-concrete stock package, by span | 81 | 486 | 4,512.02 t |
| Station-LIM primary copper/steel set, by bank | 5 | 2,430 | 22.82 t |

These are reviewable quote scopes, not complete purchasing assemblies. Their internal counts are not commercial order quantities; purchase units, supplier prices, yield, labour routes and assembly completeness remain unknown. The bogie groups are partial modeled stock, the rail entries are mass-equivalent, the concrete is nominal geometry rather than designed precast, and the LIM sets omit converters, cooling and installation. Each concrete span package carries three separate 2025 Baghdad material-plus-labour estimate scenarios at 2/4/8 skilled hours per nominal m³ with a 20% allowance. Those estimates are not supplier offers or complete process/installed cost. No approval is attached. The package candidate is bound to research candidate `9c7d0942…`; it does not transfer to the selected v0.6 reference.

Reproduce the deterministic package grouping from the sealed federated input:

```bash
./osr source procurement-bom \
  --input docs/design-engine/sourcing/packets/federated-purchasing-groups-iraq-domestic-sources-v2/input.json.gz \
  --regional-cost-reference docs/design-engine/sourcing/domestic-fabrication/regional-estimates-2025/iraq-domestic-cost-reference-2025.json \
  --output build/federated-v06-procurement-packages.json.gz
```

Reproduce the takeoff from its exact digital-twin source:

```bash
./osr source takeoff material \
  --input docs/design-engine/digital-twin/3a07936303fe5d471a88c95875e55b73b13a5cda94e98d1169f168c647766a93.tar.gz \
  --member federated-bom.json.gz --as-of 2026-10-29 \
  --output build/federated-v06-stock-takeoff.json.gz
```

The domestic fabrication screen is formula-driven:

```text
estimated unit cost = (material quantity × source rate
                     + declared labour hours × source wage/hour) × 1.20
```

For a reference tonne of reinforcing-steel input, it produces **IQD 1,231,800**, **1,276,800** and **1,366,800 per input tonne** at 4, 8 and 16 skilled-worker hours respectively. The midpoint is IQD 989,000 materials + IQD 75,000 direct labour + IQD 212,800 (20% of their IQD 1,064,000 sum). The 4/8/16-hour values are planning scenarios, not measured local process hours. The 20% is the requested unallocated planning uplift; it is not evidence for a tax, contingency, margin or factory overhead rate. Rebar cutting/bending yield, binding wire, machinery, tooling, QA, power, packaging, employer charges, transport and delivery are excluded. The estimate is attached to the exact digital-twin evaluation input for provenance, but is not assigned to a physical railway occurrence or takeoff quantity.

The source-bound [recipe files](domestic-fabrication/recipes/) and regenerated [4-hour](domestic-fabrication/estimates/current/rebar-cut-bend-04h.json), [8-hour](domestic-fabrication/estimates/current/rebar-cut-bend-08h.json) and [16-hour](domestic-fabrication/estimates/current/rebar-cut-bend-16h.json) estimate packets retain source record IDs and all omitted cost scopes. They do not close a guideway beam, car body or installed railway cost.

A second domestic unit-rate screen applies the same method to an **illustrative one nominal m³ concrete batch**. The assumed input recipe is 0.35 t ordinary cement, 0.50 m³ red sand and 0.80 m³ crushed gravel. Using the September 2026 CSO observations, direct material is IQD 46,200 + IQD 10,500 + IQD 19,200 = **IQD 75,900** per assumed batch. With 2/4/8 skilled person-hours at the Baghdad 2025 base-wage statistic of IQD 9,375/hour, the estimated totals including 20% are **IQD 113,580 / 136,080 / 181,080 per nominal m³**, respectively.

| Assumed skilled labour | Direct material | Direct base labour | 20% uplift on materials + labour | Screened unit total |
|---:|---:|---:|---:|---:|
| 2 person-hours/m³ | IQD 75,900 | IQD 18,750 | IQD 18,930 | **IQD 113,580/m³** |
| 4 person-hours/m³ | IQD 75,900 | IQD 37,500 | IQD 22,680 | **IQD 136,080/m³** |
| 8 person-hours/m³ | IQD 75,900 | IQD 75,000 | IQD 30,180 | **IQD 181,080/m³** |

This is not a concrete mix design or a precast guideway-beam price. Mix yield, strength/class, water/cement ratio, water, admixtures, grading, moisture, waste, reinforcement, prestressing, moulds, plant, utilities, QA, curing, employer-loaded labour, transport and erection remain unpriced. The labour hours are explicit scenarios, not measured factory cycles; the 20% is an unallocated planning allowance. The original per-m³ recipes remain generic unit-rate screens.

The same assumptions are now applied to the candidate-bound **1,804.8096 m³ nominal concrete volume** across 81 exact manufacturing groups and 486 engineering occurrences. The takeoff estimator verifies the complete group-volume sum and carries each group and occurrence identity into its output. It writes separate material, labour, uplift and total lines for every group as well as the aggregate, so the roll-up can be inspected without losing source traceability. Scaling the illustrative 0.35 t cement + 0.50 m³ red sand + 0.80 m³ crushed gravel per nominal m³ gives 631.683 t cement, 902.405 m³ sand and 1,443.848 m³ crushed gravel. The three direct-material estimates are IQD 136.985 million; labour at 2/4/8 skilled hours per m³ adds IQD 33.840/67.680/135.361 million; the 20% allowance yields totals of **IQD 204.990/245.598/326.815 million** (IQD 113,580/136,080/181,080 per nominal m³). These amounts are tied to the federation research candidate `9c7d0942…`, not the selected physical reference candidate. They price only the assumed material batch plus declared base labour and uplift against model volume; they are not a completed domestic fabrication or installed civil cost.

The three takeoff-mapped recipes, output packets, exact group/occurrence lists and source hashes are indexed in [validation.json](validation.json): [2-hour estimate](domestic-fabrication/estimates/current/concrete-takeoff-02h.json), [4-hour estimate](domestic-fabrication/estimates/current/concrete-takeoff-04h.json) and [8-hour estimate](domestic-fabrication/estimates/current/concrete-takeoff-08h.json). Reproduce one scenario with the `./osr source estimate takeoff` command above. The six generic unit-rate screens and three takeoff-mapped estimates remain different evidence scopes.

### Cost/weight sensitivity queue

The unresolved sourcing backlog now accepts candidate-bound `decision_sensitivity` inputs. For explicit ranges, it computes cost and mass scores as `impact-range width × uncertainty fraction × (1 + number of downstream decisions affected)`. It lists alternatives, affected simulations and requested catalogue/supplier evidence beside the score. Safety or design blockers sort ahead of economic results. Cost and mass use separate ranks and Pareto fronts rather than a made-up cost-versus-kilogram exchange rate. A `could_change_preferred` result is produced only when an explicit candidate cost margin and same-currency cost-impact range are present.

No reviewed cost/weight impact ranges or alternatives are declared in the current federated BOM. The controller reports missing inputs for the 137 evaluated unresolved groups; 6,905 other groups remain pending and have not received sensitivity scores. The queue therefore retains the existing system-category order where numeric evidence is absent. It does not claim a numeric expected value of information. The top decision packages that need declarations are the station LIM/converter alternatives, repeated guideway span/foundation, body family/manufacturing route, and complete passive bogie/brake assemblies. Their supplier evidence, quantities, and dependent structural/thermal/motion/civil reruns must be linked to the exact candidate revision before the controller can compare them.

DigiKey's [official Product Information API](https://developer.digikey.com/tutorials-and-resources/oauth-20-2-legged-flow) supports an explicit future catalogue adapter; production pricing requires a registered organization and credentials. No credentials were present during this run, and no price was fabricated. Quotation file parsers likewise produce unverified claims rather than authenticated Class A offers.

## Direct twin runs

The current 105-record offline seed includes Iraqi domestic material/wage sources, the regional cement observation and five additional local factory/fabrication leads. The vehicle-frame, 137-group balanced federation and all three laminate packets were regenerated and passed sourcing **semantic replay** against their sealed inputs and source snapshots. Packet IDs and the exact offline-seed record-set identity are in [validation.json](validation.json). Earlier 60-record and 98-record catalogue epochs remain retained in [validation-pre-domestic-iraq.json](validation-pre-domestic-iraq.json) and [validation-domestic-iraq-pre-sensitivity.json](validation-domestic-iraq-pre-sensitivity.json). Raw downloaded source documents and the SQLite database remain outside the repository.

| Input and purpose | Evaluation | Result |
|---|---|---|
| Full frame-refinement vehicle registry | 3,183 requirement groups; 40,488 physical occurrences; 16 product observations | 0 compatible supplier matches, 0 priced groups, nine disabled RFQ drafts; no complete vehicle or installed cost |
| Federated whole-railway BOM, original occurrence-level packet | 31,989 requirement groups; balanced budget evaluated 137 across propulsion, civil, body, running gear, HVAC, doors, auxiliary power, station and other | 31,852 remain pending; 0 priced groups; this historical packet predates source-declared manufacturing-group roll-up |
| Federated whole-railway BOM, manufacturing-group roll-up | 7,042 sourcing groups cover 31,989 physical scopes: 2,269 manufacturing groups retain 27,216 located occurrences, plus 4,773 unlocated accounts; balanced budget evaluates 137 | 6,905 remain pending; 0 compatible priced groups; all 137 evaluated quantities remain unknown; nine disabled RFQ drafts |
| 10 m² solid GFRP material hypothesis | 4 × 600 g/m² plies, 50% dry-glass fraction, 10% material scrap | 48 kg conditional material screen; GBP 726.65 published extension across cloth and resin lines; no order total |
| 10 m² sandwich GFRP material hypothesis | 2 × 600 g/m² plies plus declared 20 mm Gurit Corecell M80 grade at 85 kg/m³ nominal; 50% dry-glass fraction; 10% scrap | 41 kg nominal; 40.2–41.8 kg bound over the published core-density range; GBP 363.32 listed extension on priced lines; no core price |
| 10 m² higher-fibre sandwich hypothesis | Same named M80 core; two plies; 60% dry-glass fraction; 10% scrap | 37 kg nominal; 36.2–37.8 kg bound over the published core-density range; GBP 265.55 listed extension on priced lines; no core price |

The laminate rows are **new physical research proposals with ancestry to the federated candidate**. Their 10 m² basis is not measured roof CAD area; the core density, fibre fraction and scrap rate are explicit hypotheses. Resin and cloth prices cover only catalogue raw materials. Adhesive, inserts, consumables, labour, mould/tooling, inspection, transport, installation, fire/smoke, hot-wet performance and structural allowables remain unresolved. These figures cannot rank finished vehicle designs or establish a lower-cost railway.

In the current catalogue epoch, the vehicle frame still has 3,183 requirement groups and 0 exact priced matches. The federated manufacturing-group evaluation covers 31,989 physical scopes with 7,042 sourcing groups; the balanced research run evaluated 137 groups and left 6,905 pending. None of the evaluated groups has a compatible priced match, and all 137 evaluated groups still have unknown purchase quantities. The roll-up retains all 27,216 located engineering occurrences under 2,269 source-declared manufacturing groups, while keeping 4,773 unlocated accounts separate. These are practical RFQ scopes, not yet purchasable quantities or costed manufacturing assemblies. Adding Iraqi source data expands the reference library; it does not close the actual railway BOM.

## Reproducible packages

- Current 105-record source epoch: [vehicle registry](packets/frame-vehicle-iraq-domestic-sources-v2/summary.json) · [federated manufacturing-group roll-up](packets/federated-purchasing-groups-iraq-domestic-sources-v2/summary.json)
- Current 105-record source epoch: [solid laminate](packets/laminate-materials-iraq-domestic-sources-v2/solid-600gsm/summary.json) · [sandwich laminate](packets/laminate-materials-iraq-domestic-sources-v2/sandwich-600gsm/summary.json) · [higher-fibre sandwich](packets/laminate-materials-iraq-domestic-sources-v2/higher-fibre-sandwich-600gsm/summary.json)
- Earlier 60-record epoch: [vehicle registry](packets/frame-vehicle/summary.json) · [whole-railway frontier](packets/federated-balanced-frontier/summary.json) · [manufacturing-group roll-up](packets/federated-purchasing-groups/summary.json)
- Prior 98-record, pre-sensitivity epoch: [validation index](validation-domestic-iraq-pre-sensitivity.json) · [vehicle registry](packets/frame-vehicle-iraq-sources-pre-sensitivity-controller/summary.json) · [federated roll-up](packets/federated-purchasing-groups-iraq-sources-pre-sensitivity-controller/summary.json)
- Earlier 60-record epoch: [solid laminate](packets/laminate-solid-600gsm/summary.json) · [sandwich laminate](packets/laminate-sandwich-600gsm/summary.json) · [higher-fibre sandwich](packets/laminate-higher-fibre-sandwich-600gsm/summary.json)
- Domestic fabrication: [4-hour recipe and estimate](domestic-fabrication/recipes/rebar-cut-bend-04h.json) · [8-hour estimate](domestic-fabrication/estimates/current/rebar-cut-bend-08h.json) · [16-hour estimate](domestic-fabrication/estimates/current/rebar-cut-bend-16h.json)
- Concrete batch screen: [2-hour](domestic-fabrication/estimates/current/concrete-batch-02h.json) · [4-hour](domestic-fabrication/estimates/current/concrete-batch-04h.json) · [8-hour](domestic-fabrication/estimates/current/concrete-batch-08h.json)
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
./osr source estimate fabrication \
  --input docs/design-engine/sourcing/packets/federated-purchasing-groups-iraq-domestic-sources-v2/input.json.gz \
  --recipe docs/design-engine/sourcing/domestic-fabrication/recipes/rebar-cut-bend-08h.json \
  --output /tmp/osr-domestic-fabrication-estimate.json
./osr source serve
```

The SQLite database defaults to the user's XDG state directory, outside the checkout. Raw feed bytes default to the user's XDG data directory; the scheduled CI job retains only JSON status artifacts, not feed files or credentials. The Workbench binds to `127.0.0.1:8774`, uses paginated projections and denies every HTTP write method. RFQ drafts remain disabled; no supplier is contacted and no ERPNext production record or active manufacturing order is changed.

## Remaining closure work

The next high-value data is exact source-bound product mappings and supplier RFQs for the actual station-LIM winding/converter, complete passive bogie, independent brake, HVAC at Baghdad design temperature, doors/glazing, and precast guideway/foundation assemblies. The source database can retain the evidence, produce a draft request package, and invalidate dependent evaluations when an approved proposal changes. It cannot make missing geometry, source documents, supplier replies, Iraqi installed rates or physical test data appear. The whole-cell run has **zero exact priced matches**, and complete installed/whole-life cost, physical qualification and an integrated selected railway remain `unknown`.
