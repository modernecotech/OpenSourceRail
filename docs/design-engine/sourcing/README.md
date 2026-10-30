# Sourcing and cost intelligence — v0.6 research snapshot

**Snapshot prepared: 30 October 2026; source observations retain their individual dates.** This dossier connects public material/component evidence and construction benchmarks to the revision-bound v0.6 design twin. It records useful measured catalogue observations and price leads without silently substituting them into the selected vehicle. Every review packet is replayable against its sealed input, source snapshot and implementation.

## What is in the database

The current combined offline seed contains **533 immutable observations**: 83 source records, 16 product records, five published catalogue offers, three retained FX observations and 426 material, commodity, construction, wage and industrial-payroll benchmarks. This update adds four Iraqi factory leads for steel profiles, rebar, and ordinary/sulphate-resistant cement. The current candidate procurement BOM also binds ten separately identified supplementary source-only leads, outside the 533-record catalogue epoch; new leads cover cement products, local rebar and precast foundation piles, alongside aggregate production/distribution in Erbil. The frame and federated source reviews and three laminate studies remain source-bound to their earlier 529-record epoch; the current candidate procurement BOM is regenerated against the 533-record catalogue plus those separate discovery sources. Historical 305-, 307-, 416-, 513- and 529-record packets remain source-bound to their earlier epochs. The retained ECB and World Bank feed snapshot separately parsed **27 dated ECB reference-rate rows** and **two World Bank metal observations** into a local append-only database. The Central Bank of Iraq workbook adds a dated GBP/IQD conversion reference. Repeating a refresh with identical bytes reuses the source record and does not replace previous observations. Previously published packets remain source-bound to their earlier catalogue epochs.

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

The [ECB daily reference feed](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.pl.html) supplies a dated 28 October snapshot, including EUR/USD 1.1133 and EUR/GBP 0.83785. These are informational reference rates, not executable procurement conversions. A [Central Bank of Iraq daily workbook](https://cbi.iq/page/144) separately reports **IQD 1,692.216 per GBP** in its 29 October 2026 GBP selling column. That dated reference is used only to convert the listed UK laminate material extensions in the partial GFRP labour screen below. It is not an executable payment rate; channel spreads, bank eligibility, fees and settlement terms remain unknown.

Eight actual awarded Caltrans bridge-footing concrete pay items are retained in USD/CY, with original bid rates separate from the agency's adjusted rates. They are California historical comparators, **not Baghdad installed rates**. The [Iraq Tender Portal](https://itp.iq/) returned a public application shell without verified award prices. A relevant [UNGM Iraq/UNOPS notice](https://www.ungm.org/Public/Notice/221058) exposed BOQ-file leads, but the file request returned HTTP 403; the importer creates no unit-rate benchmark from those filenames. Local Iraqi concrete, steel, labour, transport, lifting, utility relocation and installation rates remain a high-priority RFQ/tender task.

### Iraqi domestic materials, wages and fabrication leads

The source catalogue includes an official [CSO September 2026 construction-material bulletin](https://mail.cosit.gov.iq/ar/constr-stat/constr-pr) and its [PDF snapshot](https://mail.cosit.gov.iq/documents/buildings/Employees%20wages/2026/%D9%86%D8%B4%D8%B1%D8%A9%20%D8%A7%D8%B3%D8%B9%D8%A7%D8%B1%20%D8%A7%D9%84%D9%85%D9%88%D8%A7%D8%AF%20%D8%A7%D9%84%D8%A7%D9%86%D8%B4%D8%A7%D8%A6%D9%8A%D8%A9%20%D9%84%D8%B4%D9%87%D8%B1%20%D8%A7%D9%8A%D9%84%D9%88%D9%84.pdf), plus an [official July 2026 CSO material and wages bulletin](https://www.cosit.gov.iq/documents/buildings/Employees%20wages/2026/%D9%86%D8%B4%D8%B1%D8%A9%20%D8%A7%D8%B3%D8%B9%D8%A7%D8%B1%20%D8%A7%D9%84%D9%85%D9%88%D8%A7%D8%AF%20%D8%A7%D9%84%D8%A7%D9%86%D8%B4%D8%A7%D8%A6%D9%8A%D8%A9%20-%20%D9%84%D8%B4%D9%87%D8%B1%20%D8%AA%D9%85%D9%88%D8%B2.pdf). The July material table reports national-market origin classes in thousand IQD; the seed normalizes them to IQD and retains the printed basis. These are statistical observations, not Baghdad installed rates or exact product quotations.

| Domestic input | Normalized observation | Source scope / limit |
|---|---:|---|
| Reinforcing steel | IQD 989,000/t | Iraqi-origin CSO September 2026 statistic; exact grade, diameter and delivery scope unspecified |
| Ordinary cement | IQD 132,000/t | Iraqi-origin CSO September 2026 national statistic; cement class/strength is not specified |
| Reported regional cement market observation | IQD 120,000/t on 8 October 2026 | Kurdistan Region bulk-market report; a regional official's reported statement, not a seller quotation, Baghdad rate or delivered price |
| Resistant cement | IQD 148,000/t | Iraqi-origin CSO September 2026 statistic; product class/strength needs supplier confirmation |
| Red sand / ordinary gravel / crushed gravel | IQD 21,000 / 21,000 / 24,000 per m³ | CSO table observation; source, grading, moisture, haulage and delivered scope open |
| Ordinary brick | IQD 184 each | Normalized from IQD 184,000 per thousand pieces |
| Skilled worker wage | Baghdad: IQD 75,000/workday = IQD 9,375/person-hour; Al-Muthanna: IQD 60,000/workday = IQD 7,500/person-hour | September 2026 CSO governorate wage rows; hourly conversion assumes 8 hours/day and excludes employer burden |
| 2025 regional material and wage series | 72 material benchmarks and 90 hourly wage benchmarks for the 15 governorates listed by CSO | [Official 2025 annual bulletin](https://www.cosit.gov.iq/documents/buildings/Employees%20wages/2025/2025%D9%86%D8%B4%D8%B1%D8%A9%20%D8%A7%D8%B3%D8%B9%D8%A7%D8%B1%20%D8%A7%D9%84%D9%85%D9%88%D8%A7%D8%AF%20%20%D9%88%D8%A7%D8%AC%D9%88%D8%B1%20%D8%A7%D9%84%D8%B9%D8%A7%D9%85%D9%84%D9%8A%D9%86%D8%A9.pdf); printed zeros remain unavailable |
| Aluminium profiles and sheet | IQD 4.60–5.50 million/t profiles; IQD 5.10–5.30 million/t sheet observations | [Ur Company posted prices](https://ur.industry.gov.iq/public/prices); alloy/temper, effective date, terms and availability are unstated |
| Rebar market indicator | IQD 931,000/t observed 29 October 2026 | [Hadeed Iraq marketplace](https://hadeediraq.com/) dashboard; not a seller-specific, grade-specific or delivery quotation |

The [CSO statistics page](https://cosit.gov.iq/ar/63-stat-ar/283-2013-02-11-03-37-09) lists monthly 2026 bulletins and annual wage/material reports. The CSO September ordinary-cement figure and the [8 October Kurdistan Region report](https://theinsightinternational.com/kurdistan-cement-steel-prices-rise-iraq-fuel-subsidy-factories-october/) are retained as separate observations because their dates, geographic coverage and evidence bases differ. The article reports a regional official's statement to Kurdistan24 that bulk cement was IQD 120,000/t, up from IQD 80,000/t. Neither figure is a Baghdad supplier quotation or installed rate. They are not averaged or used as a single candidate price; a local grade-specific supplier quotation is still required.

The same [CSO July 2026 bulletin](https://www.cosit.gov.iq/documents/buildings/Employees%20wages/2026/%D9%86%D8%B4%D8%B1%D8%A9%20%D8%A7%D8%B3%D8%B9%D8%A7%D8%B1%20%D8%A7%D9%84%D9%85%D9%88%D8%A7%D8%AF%20%D8%A7%D9%84%D8%A7%D9%86%D8%B4%D8%A7%D8%A6%D9%8A%D8%A9%20-%20%D9%84%D8%B4%D9%87%D8%B1%20%D8%AA%D9%85%D9%88%D8%B2.pdf) adds 16 origin-separated material observations and daily wages for six worker categories across 15 governorates. Its Iraqi-origin observations include ordinary cement at IQD 105,000/t, red sand at IQD 20,000/m³, crushed gravel at IQD 22,000/m³ and rebar at IQD 965,000/t. Arab- and foreign-origin price rows are retained separately; an origin category does not prove a manufacturer or place of production. Skilled daily wages are normalized by an assumed 8-hour workday: Baghdad is IQD 9,375/person-hour, Al-Muthanna IQD 7,500/person-hour, and the reported 15-governorate range is IQD 5,000–9,375/person-hour. These are statistical base wages, not factory charge-out rates; employer burden, paid time, supervision and shop overhead are absent.

The [SCOSI workshop report](https://scosi.industry.gov.iq/blog/133) records fabricated press-head components for a private aluminium extrusion press, and the [Iraqi Cement State Company page](https://icsc.industry.gov.iq/categories/details/14) lists the Samawa plant. These make useful local machining/tooling and cement-production inquiry leads. They do not verify current capacity, grade certificates, availability, delivery, railway-production capability or prices, so no offer or matched product is created from them.

The July 2026 candidate concrete estimate uses the illustrative recipe **0.35 t ordinary cement + 0.50 m³ red sand + 0.80 m³ crushed gravel per nominal m³**, for source-priced materials of IQD 64,350/m³ before labour. Applying the explicit formula `(material + skilled base wage × declared hours) × 1.20` gives:

| Labour assumption | Baghdad unit screen | Al-Muthanna unit screen |
|---:|---:|---:|
| 2 h/m³ | IQD 99,720/m³ | IQD 95,220/m³ |
| 4 h/m³ | IQD 122,220/m³ | IQD 113,220/m³ |
| 8 h/m³ | IQD 167,220/m³ | IQD 149,220/m³ |

For Iraqi-origin rebar at the CSO July 2026 IQD 965,000/t observation, the same 20% formula with 4/8/16 declared cutting/bending hours gives IQD **1,203,000 / 1,248,000 / 1,338,000 per input tonne** in Baghdad and **IQD 1,194,000 / 1,230,000 / 1,302,000** in Al-Muthanna. Arab- and foreign-origin rate observations remain separate and do not establish exact supplier or steel-grade identity. The July unit-rate packet contains these 30 rebar scenarios across all 15 listed governorates; none is mapped to candidate reinforcement demand because the latter is unresolved.

Mapped onto the same candidate takeoff's 1,804.81 m³ nominal geometry, the six regional/hours cases span IQD 179.98–301.80 million (Baghdad) and IQD 171.85–269.31 million (Al-Muthanna). The location choices are wage/material scenarios, not selected route or factory sites. Each case preserves 81 concrete manufacturing groups and 486 source occurrence IDs. This is not an approved concrete mix or a complete precast-beam estimate: reinforcement, prestress, moulds, yield, shop utilities, testing, transport, lifting, foundations, erection, maintenance, taxes and delivered quotations remain open. The 20% is an unallocated planning uplift on only the declared material and labour subtotal.

The **current September 2026** packet uses the same recipe with September Iraqi-origin material statistics: IQD 75,900/m³ before labour. With the 8-hour-normalized governorate base wages, Baghdad's 2/4/8-hour screens are IQD **113,580 / 136,080 / 181,080 per nominal m³** and Al-Muthanna's are IQD **109,080 / 127,080 / 163,080**. Applied to 1,804.8096 m³ of the research-candidate takeoff, they yield Baghdad estimates of IQD **204.990 / 245.598 / 326.815 million** and Al-Muthanna estimates of IQD **196.869 / 229.355 / 294.328 million**. All six preserve 81 manufacturing groups and 486 engineering occurrences. The 20% covers only modeled materials and assumed direct base-wage labour; these are not designed concrete, completed precast or installed costs.

The same current packet now adds **42 Iraq domestic aluminium raw-stock sensitivity cases** for the exact federated takeoff. The `aluminium_reference` rollup is 17,535.607 kg across 1,164 groups and 23,286 occurrences; the `6082-T6-proposed` rollup is 1,652.057 kg across 312 groups and occurrences. For each, seven Ur Company posted profile/sheet forms are priced separately at 8/16/32 assumed fabrication hours per tonne, using the Baghdad September skilled-worker base-wage proxy. The resulting raw-stock plus labour plus 20% screens are IQD **98.4–122.0 million** for the generic body aluminium rollup and **9.3–11.5 million** for the proposed secondary. The takeoff has no profile/sheet quantity split, no purchased tonnes or yield, and no declared shop hours. Ur does not state structural alloy/temper or confirm 6082-T6; these are not accepted product matches or quotations. Each estimate retains the exact candidate and takeoff IDs, and the material-demand BOM now links the alternatives to their corresponding lines. See the [current regional packet](domestic-fabrication/regional-estimates-2026-september-v6/iraq-domestic-cost-reference-2026-09.json) and its [file-hash index](domestic-fabrication/regional-estimates-2026-september-v6/manifest.json).

### Additional material benchmarks for domestic fabrication

The new official [CSO 2024 private-sector building report](https://cosit.gov.iq/documents/buildings/Private%20sector%20buildings/%D8%A7%D9%84%D9%82%D8%B7%D8%A7%D8%B9%20%D8%A7%D9%84%D8%AE%D8%A7%D8%B52024%20.pdf) provides a second, independent Iraqi material-price basis. Table 15 reports estimated building material costs and quantities. Dividing those fields gives historical unit ratios; these are modelled statistical values, not observed transactions or supplier quotations. The report's quantities draw on 2024 building permits, market prices/wages and material-use ratios from a 2012 survey, and its coverage excludes the Kurdistan Region.

| CSO 2024 Table 15 material | Baghdad derived ratio | 15-governorate aggregate ratio | Use / limitation |
|---|---:|---:|---|
| Ordinary cement | IQD 115,000/t | IQD 114,672.74/t | Grade/strength and delivered scope unspecified |
| Resistant cement | IQD 140,000/t | IQD 131,703.83/t | Grade/strength and delivered scope unspecified |
| Red sand | IQD 22,000/m³ | IQD 18,504.52/m³ | Grading, moisture and haulage unspecified |
| Black sand | IQD 20,000/m³ | IQD 18,116.63/m³ | Grading, moisture and haulage unspecified |
| Normal grit | IQD 20,000/m³ | IQD 19,985.61/m³ | Not assumed equivalent to 2025 crushed gravel |
| Broken grit | IQD 22,000/m³ | IQD 19,877.99/m³ | Product grading and delivery scope unspecified |
| Iron/reinforcement row | IQD 1,128,000/t | IQD 1,083,181.40/t | Exact steel product form and grade unresolved |

The resulting [`iraq-material-cost-history-crosscheck-2024.json`](domestic-fabrication/regional-estimates-2025-v6/iraq-material-cost-history-crosscheck-2024.json) applies a consistent illustrative recipe of 0.35 t cement, 0.50 m³ red sand and 0.80 m³ aggregate per nominal m³. It holds the 2025 Baghdad base wage (IQD 9,375/hour) and requested 20% uplift constant while changing only the material-price basis.

| Material basis | 2 labour h/m³ | 4 labour h/m³ | 8 labour h/m³ |
|---|---:|---:|---:|
| 2024 statistical material ratios + 2025 wage | IQD 103,200 | IQD 125,700 | IQD 170,700 |
| 2025 CSO material rates + 2025 wage | IQD 114,720 | IQD 137,220 | IQD 182,220 |

Formula: `(material quantities × source rates + assumed person-hours × IQD 9,375/hour) × 1.20`. The hours are scenarios, not measured local process routes. These mixed-period comparisons are historical sensitivity estimates only; normal grit is not silently treated as crushed gravel, and neither result is a designed concrete mix, precast beam price or candidate-installed civil cost. The 20% remains an unallocated allowance, not a sourced overhead or margin.

The CSO rebar statistic and the marketplace indicator differ in date and scope. They are retained separately and are not blended into a fabricated quote. The public [Cement Producers Association directory](https://cpai.iq/companies) identifies Iraqi cement producers for RFQ follow-up. More domestic manufacturing leads are [Star Steel Iraq](https://starsteeliraq.com/manufacturing/) and [Alpha Steel](https://alphasteel.iq/) for reinforcing steel; [Dijla Precast](https://dijla-precast.com/production-lines/), [Karbala Precast](https://karbala-company.com/), [Al-Fayha](https://www.al-fayhagroup.net/products/prefabricated-building-products), [Al-Burhan](https://www.alburhangroup.com/concrete-precast-factory.php) and [Al-Kanz](https://alkanz.iq/about-us/) for precast/piles/girders. Their public pages establish supplier leads only. Request exact grades, certificates, capacity allocation, schedule, warranty, transport and binding project quotations before using them in a candidate estimate. The regional [FRP Technology](https://www.frptechnology.com/) lead advertises an Iraq distribution network, but this does not establish Iraqi GFRP feedstock manufacture or local stock.

Additional domestic production leads are now retained as distinct sources:

| Domestic source | Publicly described capability | Current evidence boundary |
|---|---|---|
| [Iraqi Cement State Company](https://icsc.industry.gov.iq/) | Government cement plants and ordinary/resistant cement production plans | Plant availability, certified grade, delivery and current project price remain unconfirmed |
| [State Company for Steel Industries](https://scosi.industry.gov.iq/) | Steel structures, foundry, crane/tower/galvanizing, mechanical workshop and quality-control units | Capability lead only; no railway component scope, current capacity allocation or quotation |
| [Al Anmaa steel plant](https://ahfed.org.iq/factories/alanmaa/) | Foundation page describes a Khor Al-Zubair EAF/continuous-casting plant and reinforcing bar | Its 800,000 t/year figure is a company-reported capacity claim; current output, grade certificates and availability are unverified |
| [Darin Steel](https://www.darinsteel.com/) | Erbil rebar manufacturer; company pages cite ASTM A615/A706 and Grade 60 product information | Rebar is only a lead for separately unresolved reinforcement; current batch certificates, size, project allocation, delivery and price need RFQ |
| [Med Steel](https://www.medsteel.com/) | Erbil producer of locally rolled flat, square, angle, U and T sections as well as rebar | Exact grade, dimensional tolerances, project availability, and fatigue-critical vehicle or bogie suitability remain unverified |
| [Saman Cement](https://www.samancement.iq/default.aspx) | Al-Muthanna producer listing OPC and sulphate-resistant cement products | Grade/batch certificates, availability, price, bulk terms, and the assumed concrete recipe still need supplier and mix-design confirmation |
| [Delta Cement](https://delta-cement.com/ar/products.aspx) | Bazian producer listing OPC, sulphate-resistant, and limestone cement grades | No source price is attached; product certificate, current delivery, mix compatibility and project quotation remain open |
| [Iraq Alhur GRP factory](https://iraqalhur-grp.iq/en/) | Baghdad/Al-Nahrawan GRP pipe manufacture | Pipe capability does not establish passenger-body panel capability or rail structural/fire qualification |
| [Al-Khassaki aluminium factory project](https://akg-eng.net/al-khassaki-factory-for-melting-and-extruding-aluminum-sections/) | Project page describes planned aluminium melting/extrusion of profiles and sheets | The page states 75% progress; commissioning and operating capacity are not established |

These entries help route domestic procurement and fabrication research. They are not available-to-buy records, validated capacity data, certified component designs or prices. In particular, the aluminium project is not counted as operating capacity and the GRP pipe plant is not treated as a source of qualified vehicle-body panels.

The current source layer adds three more local composites leads: [NUBIN](https://www.nubingrc.com/) describes GRP/GFRP façade design and manufacture in Erbil; [Abr AlQamar](https://abralqamar.com.iq/products/) lists polyester resin and epoxy resin/curing agents; and [Al-Mniee](https://almnieetrading.com/) describes polymer raw-material supply from Baghdad. They suggest possible local fabrication and materials RFQs, but do not establish a railway-panel process, a usable material grade, compatible glass reinforcement, local stock, current capacity or a price. No locally made continuous glass-fibre cloth or rail-qualified composite system is verified in this source set. The three entries are supplier leads only and create no offers.

Four additional local aluminium manufacturing leads are now recorded: [Asia Aluminum](https://www.asiaaluminum.net/) in Sulaymaniyah, [Alko Aluminum](https://rojan.com.tr/company/alkoaluminum) at Duhok Industrial Site, [Baxi Siwail](https://www.baxisiwail.com/) in Sulaimani, and [IIALCO](https://dijlagroup.com/iialco/) in Erbil. Their public pages describe extrusion/profile or flat/sandwich-panel capabilities; some pages focus on architectural products. Exact alloys, tempers, dimensions, structural allowables, binding prices, current capacity and railway suitability remain unverified. These records create no supplier offers or product matches. The current Ur Company posted price remains the only local aluminium price input to the present profile/sheet labour sensitivities.

Five further domestic fabrication routes were checked against primary company or government pages on 30 October 2026:

| Source | Publicly described route | What still needs confirmation |
|---|---|---|
| [Iraqi Industry Platform](https://iip.industry.gov.iq/) | Ministry industrial directory, factory map, product discovery and manufacturer contact/RFQ routes | Supplier identity, current production, product specifications, capacity, eligibility and quotations for each listing |
| [Duraid Al Sudani](https://duraidalsudani.com.iq/home-en/) | Baghdad metal sections, cable trays, conduits, distribution panels and custom metal fabrication | Alloy/grade, process envelope, capacity, certifications, railway scope and quote |
| [MS Company](https://www.ms.com.iq/) | Power cables, bare conductors and busbars in Bazian/Sulaimaniyah | Conductor grade and size, standards, tests, capacity, availability and quote |
| [Diala State Company](https://www.iitp.mot.gov.iq/Home/CompanyProfile?AspxAutoDetectCookieSupport=1&Id=32) | Government trade-portal company profile lists distribution/power transformers and electrical meters | Exact models, ratings, standards, plant status, compatibility and quote |
| [Qaiwan Steel Factory](https://qsf-iq.com/) | Manufacturer page lists rebar sizes 10–32 mm and states 400,000 t/year capacity | Capacity is self-reported; confirm current output, grade certificates, allocation, delivery and quote |

These are source leads only. The industrial directory is a discovery and RFQ route, not a supplier offer. The three supplier pages remain self-described capability information, while Diala is a government trade-portal listing; none contributes a product row, compatible match, supplier price or local-content credit. The 20% cost uplift used by the domestic fabrication screens is applied only to cited material observations plus assumed direct base-wage hours. It does not cover validated overhead, profit, tax, equipment, tooling, QA, utilities, yield, transport or installation.

Two additional domestic electrical-material leads were checked on 30 October 2026:

| Source | Publicly described route | What still needs confirmation |
|---|---|---|
| [Alrowad](https://www.alrowadcable.com/about-us/) | Manufacturer page describes low/medium-voltage cables, overhead conductors and renewable-energy cables at a southern Baghdad facility | Exact conductor construction, copper grade, sizes, standards, test certificates, current capacity, availability and quoted price |
| [Copper and Mechanical Industries Company](https://dici.gov.iq/en/activities/d72e392e-4b5b-4ea0-9cdc-124fcd65fcc8) | Iraqi Defence Industries Commission's 2023 notice described an intended copper-wire production line | Commissioning/current operation, conductor size/grade, output, quality tests, supply allocation and price |

The DICI notice is deliberately classified as a planned industrial lead; it is not counted as current domestic wire production. Neither source creates a product match or a price. The existing NUBIN source record already covers local architectural GRP/GFRP façade fabrication; no duplicate record was added, and façade work does not establish rail-body capability.

The latest source extension adds a verified [Baghdad ready-mix capability lead](https://scdpi.industry.gov.iq/en/page/15) from the Ministry of Industry's General Company for Design and Projects Implementation. Its official page describes C15/C25/C30/C36 production, transfer, pumping and laboratory testing, with a company-stated 60–120 m³/h capacity. No current unit price, mix design, delivery condition, site allocation or precast beam offer is published. The capacity is therefore an RFQ and throughput lead only; it is not used as a price or full span-production rate.

The current Iraqi discovery layer adds six fabrication and sourcing leads: [SCOSI foundry and forging](https://scosi.industry.gov.iq/page/76/مصنع-السباكة-والطرق), [Al-Burhan sleeper and precast operation](https://alburhangroups.com/our-factory/), [Karbala Precast bridge beams](https://www.karbala-company.com/products.php), [Ittifaq steel mesh](https://ittifaq-brc.com/en/home/), [NCPI chemical and plastics production](https://ncpi.com.iq/%D9%85%D9%86-%D9%86%D8%AD%D9%86/) and [Al-Qader steel supply](https://al-qader-group.iq/en/about-us/). Their public pages point to potentially useful casting/forging, sleepers, prestressed beams, mesh, chemicals/plastics and steel distribution. They do not supply priced, compatible railway assemblies; exact grade, domestic origin, live capacity, certification and delivery scope need confirmation. The source registry treats them as leads, not offers.

The official [CSO industrial-establishment indicators](https://cosit.gov.iq/ar/2013-03-29-08-30-31) report 2024 average annual worker pay of IQD 12.5 million in large and IQD 6.3 million in medium industrial establishments. These are retained as `person-year` benchmarks. They are not converted to hourly rates because paid hours, occupation, location and employer-cost scope are absent; the fabrication estimates continue using explicit hours with the separate construction-worker wage observations.

The [CSO 2025 non-oil import report](https://cosit.gov.iq/documents/trade/foreign%20trade/%D8%AA%D9%82%D8%B1%D9%8A%D8%B1%20%D8%A7%D9%84%D8%A7%D8%B3%D8%AA%D9%8A%D8%B1%D8%A7%D8%AF%D8%A7%D8%AA25.pdf) is downloaded, SHA-256 checked (`d440c32056a52c2b58277878041028270ac300ce44bca5665f716b773d8bda86`), and selected Table 10 rows visually reviewed. The report says imports are valued CIF, grouped by origin and HS 2017 from customs data, with Kurdistan Region excluded from its customs coverage. Eight national HS-group rows now have source-linked USD/kg and IQD/kg import unit-value benchmarks: epoxy resin (39073000), glass combed fibres/wraps (70191200), copper wire over 6 mm (74081100), four aluminium profile/sheet groups (76042100, 76042900, 76069100, 76069200), and 10–32 mm reinforcing steel (72141020). Each is national import value divided by the report's Weight(K.G.) total, not a supplier price. Source totals, weights, HS codes and printed page references are retained in the benchmark records; the separate Quantity field is not used as the mass denominator.

For domestic aluminium processing research, the [imported-stock sensitivity packet](domestic-fabrication/cso-imported-aluminium-fabrication-sensitivity-2025-2026.json) combines each HS-group IQD/t import value with 8/16/32 assumed local skilled hours/t at the September 2026 Baghdad CSO base-wage proxy (IQD 9,375/h), then applies the requested 20% to material plus direct labour. Its generic one-tonne screened rates span IQD **5.80–8.64 million/t** across the four HS forms. This is a mixed-period imported-stock plus assumed Iraqi labour screen; the hours are not measured shop routes and the 20% is unallocated. It is not bound to the vehicle BOM because profile/sheet mix, alloy/temper, gross purchasing mass, yield and product identity remain unknown. It excludes tooling, energy, consumables, QA, finishing, taxes/duties, inland delivery and installation. The [State Company for General Industries (Ur Company)](https://ur.industry.gov.iq/public/prices) also lists aluminium profiles/sheets and copper wire, winding-wire and cable lines; the copper line's price basis and exact unit/specification remain unclear, so those lines are retained as local sourcing leads and are not imported as offers.

The Ministry of Construction's [September 2026 notice](https://istisharat.moch.gov.iq/2026/09/27/%D9%85%D8%AF%D9%8A%D8%B1-%D8%B9%D8%A7%D9%85-%D8%A7%D9%84%D8%A3%D8%B3%D8%AA%D8%B4%D8%A7%D8%B1%D8%A7%D8%AA-%D8%A7%D9%84%D9%87%D9%86%D8%AF%D8%B3%D9%8A%D8%A9-%D9%8A%D8%AD%D8%B6%D8%B1-%D8%A7%D9%84%D8%A7/) says an indicative construction-price bulletin and unified BOQ analysis are being prepared; it supplies no rates yet. The [Iraqi Cement State Company product page](https://icsc.industry.gov.iq/products) exposes price images without extractable product, unit, date or amount, so it remains an unpriced source lead. The [National Investment Commission's industrial-sector opportunities](https://investpromo.gov.iq/investment-opportunities-in-the-industrial-sector/) identify factory rehabilitation and upgrade projects, including cable, aluminium, pipe, cement and glass facilities. These are investment opportunities, not proof that those facilities currently operate or can supply the railway.

### Regional material + labour estimates

The regional price library uses the CSO 2025 Iraqi-origin material rows and daily wage averages for the 15 governorates in the bulletin. The bulletin excludes Kurdistan Region governorates. Missing source-table values are not interpreted as zero: concrete estimates are held for Kirkuk, Wasit and Salah al-Din because at least one required material price is not reported. Annual market averages are not exact supplier quotations, and wage rates are base averages rather than employer-loaded factory charge-out rates.

The reproducible [regional cost packet](domestic-fabrication/regional-estimates-2025-v6/iraq-domestic-cost-reference-2025.json) contains 102 unit-rate scenarios: concrete batching for 12 governorates, rebar cut/bend for all 15, nine Baghdad aluminium-profile processing sensitivities across three Ur Company finishes, and 12 Baghdad sheet-processing sensitivities across four posted sheet forms. Each uses an explicit material input, labour-hour scenario and a 20% uplift on direct material plus direct base wage. The labour hours are planning sensitivities, not timed shop routes; the uplift is unallocated and is not verified as overhead, profit, tax or contingency.

| Domestic fabrication scenario | Declared input basis | Estimated rate with 20% uplift |
|---|---|---:|
| Baghdad concrete batching, 2 / 4 / 8 skilled h per nominal m³ | 0.35 t ordinary cement + 0.50 m³ red sand + 0.80 m³ crushed gravel; 2025 Baghdad material and wage statistics | IQD 114,720 / 137,220 / 182,220 per nominal m³ |
| Baghdad rebar cutting/bending, 4 / 8 / 16 skilled h per input tonne | 1 t at the 2025 Iraqi-origin Baghdad rebar statistic plus declared labour | IQD 1,296,600 / 1,341,600 / 1,431,600 per tonne |
| Baghdad non-oxidized profile processing, 8 / 16 / 32 h/t | 1 t at Ur Company posted price plus 2025 Baghdad base-wage proxy | IQD 5,610,000 / 5,700,000 / 5,880,000 per tonne |
| Baghdad oxidized profile processing, 8 / 16 / 32 h/t | 1 t at Ur Company posted price plus 2025 Baghdad base-wage proxy | IQD 6,330,000 / 6,420,000 / 6,600,000 per tonne |
| Baghdad spray-painted profile processing, 8 / 16 / 32 h/t | 1 t at Ur Company posted price plus 2025 Baghdad base-wage proxy | IQD 6,690,000 / 6,780,000 / 6,960,000 per tonne |
| Baghdad hard sheet, 0.6–0.9 mm, 8 / 16 / 32 h/t | 1 t at Ur Company posted hard-sheet price plus 2025 Baghdad base-wage proxy | IQD 6,330,000 / 6,420,000 / 6,600,000 per tonne |
| Baghdad hard sheet, 1 mm+, 8 / 16 / 32 h/t | 1 t at Ur Company posted hard-sheet price plus 2025 Baghdad base-wage proxy | IQD 6,210,000 / 6,300,000 / 6,480,000 per tonne |
| Baghdad annealed sheet, 0.6–0.9 mm, 8 / 16 / 32 h/t | 1 t at Ur Company posted annealed-sheet price plus 2025 Baghdad base-wage proxy | IQD 6,450,000 / 6,540,000 / 6,720,000 per tonne |
| Baghdad annealed sheet, 1 mm+, 8 / 16 / 32 h/t | 1 t at Ur Company posted annealed-sheet price plus 2025 Baghdad base-wage proxy | IQD 6,330,000 / 6,420,000 / 6,600,000 per tonne |

These sheet estimates use the Ur Company page’s four price rows (IQD 5.10–5.30 million/t) as raw-stock inputs. The page does not identify alloy or temper standards, establish whether the labels correspond to structural properties, or specify availability, yield, cutting/forming operations, joining, tooling or delivery. The output is therefore raw-stock plus assumed labour, not a formed panel price or vehicle-body estimate. Do not use it to replace the aluminium body candidate’s engineering masses or qualifications.

The Baghdad concrete scenarios are also applied to the exact research-candidate nominal-volume takeoff, preserving its 81 manufacturing groups and 486 original engineering occurrences. The 2025 material-rate packet estimates IQD **207.05–328.87 million** for the modeled 1,804.81 m³ nominal concrete volume across the 2/4/8-hour cases. That is a recipe-based estimate for a research candidate, not a structural mix, complete precast span, installed civil price or selected-reference cost. It excludes rebar, prestress, moulds, factory utilities, QA, handling, transport, piers, foundations, erection and maintenance. See the [2 h](domestic-fabrication/regional-estimates-2025-v6/baghdad-concrete-takeoff-2h.json), [4 h](domestic-fabrication/regional-estimates-2025-v6/baghdad-concrete-takeoff-4h.json) and [8 h](domestic-fabrication/regional-estimates-2025-v6/baghdad-concrete-takeoff-8h.json) group-mapped packets.

Regenerate the regional unit-rate scenarios and group-mapped Baghdad concrete packets from the exact takeoff with:

```bash
./tools/automation/osr-python -m engineering.sourcing.iraq_cost_scenarios \
  --takeoff docs/design-engine/sourcing/material-takeoff/federated-v06-stock-takeoff-v5.json.gz \
  --output build/iraq-domestic-cost-scenarios
```

### Candidate material takeoff

`./osr source takeoff material` now produces a material-oriented roll-up from the exact federated railway BOM. The [source-bound takeoff](material-takeoff/federated-v06-stock-takeoff-v5.json.gz) retains all 2,269 manufacturing-group identities and all 27,216 located engineering occurrences, while leaving the 4,773 unlocated accounts separate. It derives **4,780.58 t of located gross stock mass** and **1,804.81 m³ of nominal concrete stock geometry** from the candidate bundle. These are modeled stock quantities; they are not weighed installed mass, purchase orders, or complete project quantities.

| Material family | Candidate stock quantity | Sourced price reference | Treatment |
|---|---:|---:|---|
| Station LIM copper conductor | 9.35424 t across five banks | USD 14,474/t; raw commodity extension USD 135,393.27 | World Bank September 2026 copper benchmark; winding conductor, insulation, winding labour, converter, cooling and installation remain unpriced |
| Vehicle-body aluminium reference | 17.53561 t | USD 3,283/t; raw commodity extension USD 57,569.40 | World Bank September 2026 aluminium benchmark; sheet/extrusion mix, alloy, forming, joining, finish and installation remain unpriced |
| Proposed 6082-T6 onboard secondary | 1.65206 t | USD 3,283/t; raw commodity extension USD 5,423.70 | Primary aluminium benchmark only; alloy/temper premium, plate form, machining and assembly remain unpriced |
| Concrete guideway stock | 4,512.02 t; 1,804.81 m³ | Illustrative raw-material + labour scenario: IQD 113,580–181,080 per nominal m³ | No design mix, finished concrete offer, reinforcement/prestress closure, or local installed concrete quote |
| 60E1-equivalent rail | 195.08 t | No compatible rate | The retained ArcelorMittal catalogue observation is for a different rail profile; no price is transferred |

The metal extensions are raw-commodity comparisons, **not accepted supplier matches, product prices, cost bounds or installed-cost estimates**. The takeoff links the Baghdad CSO September 2026 skilled-worker wage observation of IQD 9,375/person-hour, normalized from the reported daily average using an 8-hour day. The 2,269 groups do not declare measured labour hours. A separate recipe applies explicit 2/4/8-hour scenarios only to the concrete roll-up; all other manufacturing groups remain without calculated labour or fabrication costs. The rebar and concrete examples below are material-plus-labour scenarios, and their hours and mix quantities remain planning assumptions.

### Draft procurement-package BOM

The retained [v6 package packet](procurement-bom/federated-v06-research-packages-v6.json.gz) groups all **27,216 located stock occurrences** in the federated research candidate into 191 hierarchy-based sourcing-package candidates. It preserves each engineering occurrence, manufacturing-group identity, and related procurement/manufacturing task ID. The **4,773 unlocated obligations remain separate** and do not enter package masses or quantities.

| Draft sourcing scope | Packages | Located occurrences | Modeled gross stock mass |
|---|---:|---:|---:|
| Vehicle-body-system stock kit, by car | 6 | 23,466 | 19.21 t |
| Passive-bogie stock package | 12 | 360 | 29.79 t |
| Passive-secondary stock kit, by car | 6 | 312 | 1.65 t |
| Rail stock pair, by span | 81 | 162 | 195.08 t |
| Nominal-concrete stock package, by span | 81 | 486 | 4,512.02 t |
| Station-LIM primary copper/steel set, by bank | 5 | 2,430 | 22.82 t |

These are reviewable quote scopes, not complete purchasing assemblies. Their internal counts are not commercial order quantities; purchase units, supplier prices, yield, labour routes and assembly completeness remain unknown. The bogie groups are partial modeled stock, the rail entries are mass-equivalent, the concrete is nominal geometry rather than designed precast, and the LIM sets omit converters, cooling and installation. The current [v18 procurement packet](procurement-bom/federated-v06-research-packages-v18.json.gz) attaches six September 2026 Baghdad/Al-Muthanna material-plus-labour scenarios at 2/4/8 assumed skilled hours per nominal m³ to each of the 81 concrete spans, with a 20% uplift. It also attaches an illustrative ingredient takeoff to the exact span geometry: 631.68336 t cement, 902.4048 m³ red sand and 1,443.84768 m³ crushed gravel, using the cited 0.35/0.50/0.80 recipe coefficients and September Iraqi-origin CSO material rates. The aggregate direct-material extension is IQD 136,985,048.64; the per-span values reconcile to the material component of each labour scenario. This is a quantity and rate screen, not a designed concrete mix, order quantity or complete precast/installed cost. Yield, grade, grading, delivery and product compatibility remain unknown. The 20% uplift applies to declared material plus assumed base-wage labour. No approval is attached. The package candidate is bound to research candidate `9c7d0942…`; it does not transfer to the selected v0.6 reference.

The current [v18 procurement packet](procurement-bom/federated-v06-research-packages-v18.json.gz) preserves 191 quote-scope drafts and adds eight material-demand lines. The lines aggregate 2,269 manufacturing groups and 27,216 located occurrences across concrete, rail-equivalent mass, aluminium, GFRP, steel, passive secondary, copper and station-primary steel. Seven lines have Iraqi source leads; its source registry contains 93 exact source records (83 from the offline catalogue and ten supplementary Iraqi discovery sources). The packet records 43 non-additive source-lead associations across seven material families. New first-party source leads identify cement product families from [Lafarge Iraq](https://www.lafarge-iraq.com/en/Our-Cement), [Alpha Steel](https://alphasteel.iq/) rebar product claims, and [Al-Kanz](https://alkanz.iq/home-english/) precast-pile capability. Cement grade/batch compatibility is unconfirmed; Alpha Steel's rebar is only a lead for unlocated reinforcement, with no rebar quantity included in the nominal-concrete line; Al-Kanz piles are not attached to an unselected foundation design. Darin rebar and Saman/Delta cement leads remain linked only as context for separate, unlocated reinforcement or concrete-ingredient inquiries; Med Steel section stock is a generic fabrication lead, not a bogie match. The 60E1 rail mass-equivalent line has no mapped Iraqi rail-profile lead. Two aluminium lines carry 21 separate raw-stock material-plus-labour-plus-20% sensitivities each, keyed to the exact source takeoff. Profile/sheet, alloy/temper compatibility and purchase yield remain unresolved, so these alternatives are not quoted prices or accepted product matches. The packet adds the exact 81-span ingredient takeoff described above and retains 191 draft scopes, 4,773 unlocated obligations and zero compatible priced packages. Source-linked quantities still do not represent commercial purchase units, compatible priced supplier matches, manufacturing routes or finished assembly costs. The package retains its source/member mass residual as an audit check.

Reproduce the current package from the exact digital-twin source and recipe:

```bash
./osr source procurement-bom \
  --input docs/design-engine/digital-twin/3a07936303fe5d471a88c95875e55b73b13a5cda94e98d1169f168c647766a93.tar.gz \
  --member federated-bom.json.gz \
  --regional-cost-reference docs/design-engine/sourcing/domestic-fabrication/regional-estimates-2026-september-v6/iraq-domestic-cost-reference-2026-09.json \
  --concrete-material-recipe docs/design-engine/sourcing/domestic-fabrication/takeoff-recipes/concrete-material-inputs-2026-09.json \
  --output build/federated-v06-research-packages-v18.json.gz
```

Reproduce the historical deterministic package grouping from the sealed federated input:

```bash
./osr source procurement-bom \
  --input docs/design-engine/sourcing/packets/federated-purchasing-groups-iraq-domestic-sources-v6/input.json.gz \
  --regional-cost-reference docs/design-engine/sourcing/domestic-fabrication/regional-estimates-2026-july-v2/iraq-domestic-cost-reference-2026-07.json \
  --output build/federated-v06-procurement-packages.json.gz
```

Reproduce the takeoff from its exact digital-twin source:

```bash
./osr source takeoff material \
  --input docs/design-engine/digital-twin/3a07936303fe5d471a88c95875e55b73b13a5cda94e98d1169f168c647766a93.tar.gz \
  --member federated-bom.json.gz --as-of 2026-10-30 \
  --output build/federated-v06-stock-takeoff-v5.json.gz
```

The domestic fabrication screen is formula-driven:

```text
estimated unit cost = (material quantity × source rate
                     + declared labour hours × source wage/hour) × 1.20
```

For a reference tonne of reinforcing-steel input, the September 2026 material and Baghdad wage inputs produce **IQD 1,231,800**, **1,276,800** and **1,366,800 per input tonne** at 4, 8 and 16 skilled-worker hours. The 8-hour case is IQD 989,000 material + IQD 75,000 direct base labour + IQD 212,800 (20% of their IQD 1,064,000 sum). The 4/8/16-hour values are planning scenarios, not measured local process hours. The 20% is the requested unallocated planning uplift; it is not evidence for a tax, contingency, margin or factory overhead rate. Rebar cutting/bending yield, binding wire, machinery, tooling, QA, power, packaging, employer charges, transport and delivery are excluded. The estimate is attached to the exact digital-twin evaluation input for provenance, but is not assigned to a physical railway occurrence or takeoff quantity.

The source-bound [recipe files](domestic-fabrication/recipes/) and regenerated [4-hour](domestic-fabrication/estimates/current/rebar-cut-bend-04h-v6.json), [8-hour](domestic-fabrication/estimates/current/rebar-cut-bend-08h-v6.json) and [16-hour](domestic-fabrication/estimates/current/rebar-cut-bend-16h-v6.json) estimate packets retain source record IDs and omitted cost scopes. The current September material observation is IQD 989,000/t; the resulting material + labour + 20% screens are IQD 1,231,800 / 1,276,800 / 1,366,800 per input tonne at 4/8/16 assumed hours. They do not close a guideway beam, car body or installed railway cost.

A second domestic unit-rate screen applies the same method to an **illustrative one nominal m³ concrete batch**. The assumed input recipe is 0.35 t ordinary cement, 0.50 m³ red sand and 0.80 m³ crushed gravel. Using the September 2026 CSO observations, direct material is IQD 46,200 + IQD 10,500 + IQD 19,200 = **IQD 75,900** per assumed batch. With 2/4/8 skilled person-hours at the September Baghdad base-wage statistic of IQD 9,375/hour, the estimated totals including 20% are **IQD 113,580 / 136,080 / 181,080 per nominal m³**, respectively.

| Assumed skilled labour | Direct material | Direct base labour | 20% uplift on materials + labour | Screened unit total |
|---:|---:|---:|---:|---:|
| 2 person-hours/m³ | IQD 75,900 | IQD 18,750 | IQD 18,930 | **IQD 113,580/m³** |
| 4 person-hours/m³ | IQD 75,900 | IQD 37,500 | IQD 22,680 | **IQD 136,080/m³** |
| 8 person-hours/m³ | IQD 75,900 | IQD 75,000 | IQD 30,180 | **IQD 181,080/m³** |

This is not a concrete mix design or a precast guideway-beam price. Mix yield, strength/class, water/cement ratio, water, admixtures, grading, moisture, waste, reinforcement, prestressing, moulds, plant, utilities, QA, curing, employer-loaded labour, transport and erection remain unpriced. The labour hours are explicit scenarios, not measured factory cycles; the 20% is an unallocated planning allowance. The original per-m³ recipes remain generic unit-rate screens.

The same assumptions are applied to the candidate-bound **1,804.8096 m³ nominal concrete volume** across 81 manufacturing groups and 486 engineering occurrences. The estimator verifies the full group-volume sum and carries each group and occurrence identity into its output. The September recipe scales to 631.683 t cement, 902.405 m³ sand and 1,443.848 m³ crushed gravel. The material estimate is IQD 136.985 million; labour at 2/4/8 skilled hours per m³ adds IQD 33.840/67.680/135.361 million; the 20% allowance yields Baghdad totals of **IQD 204.990/245.598/326.815 million** (IQD 113,580/136,080/181,080 per nominal m³). Al-Muthanna totals are **IQD 196.869/229.355/294.328 million** (IQD 109,080/127,080/163,080 per nominal m³). These remain tied to federation research candidate `9c7d0942…`, not the selected physical reference. They price only recipe materials plus assumed base labour and uplift; they are not complete domestic fabrication or installed civil costs.

The three takeoff-mapped recipes, output packets, exact group/occurrence lists and source hashes are indexed in [validation.json](validation.json): [2-hour estimate](domestic-fabrication/estimates/current/concrete-takeoff-02h-v6.json), [4-hour estimate](domestic-fabrication/estimates/current/concrete-takeoff-04h-v6.json) and [8-hour estimate](domestic-fabrication/estimates/current/concrete-takeoff-08h-v6.json). Reproduce one scenario with the `./osr source estimate takeoff` command above. The six generic unit-rate screens and three takeoff-mapped estimates remain different evidence scopes. `validation.json` is retained as its original source-bound index; the latest 529-record epoch and regenerated packets are indexed by [validation-current.json](validation-current.json).

### Additional domestic material leads

Three new Iraqi supplier leads point to [Hemn Group EPS panels](https://www.hemngroup.com/factories/eps-factory/en), [Helal Group polyurethane foam](https://helal-group.com/foam/) and [Qatral aluminium ingots/alloys](https://qatral.com/about-us-2/). The company pages report (respectively) an EPS-panel line claiming 10 t/day, polyurethane foam at stated density ranges of 12–45 kg/m³, and aluminium ingots/alloys/anode blocks produced or supplied from Erbil. These are discovery leads only. They do not provide a compatible priced product, confirmed available capacity, railway structural/fire properties or an exact core alloy/grade. EPS and upholstery PU are not treated as structural sandwich core. The [current validation index](validation-current.json) retains their source IDs and confirms zero products, offers, benchmarks or candidate matches.

### Iraqi trailer and crane rental sensitivity

The official [Fa'o General Engineering Company Contracts Section](https://faoco.moch.gov.iq/ar/node/69) lists contract number 18 dated 27 September 2026: six trailers plus one crane, with IQD 1,150,000 per trailer trip and IQD 500,000 per crane-day. The source does not state trailer payload or dimensions, haul distance, crane configuration/rating/radius, mobilisation, fuel, tax or current availability. The record is stored as an optional, separate source seed at [`iraq-transport-rental-2026-09.json`](../../../engineering/sourcing/data/iraq-transport-rental-2026-09.json); it is not a compatible supplier product or a default catalogue price match.

The new [candidate-bound logistics packet](domestic-fabrication/logistics-2026-september-v1/README.md) cross-references the exact v16 procurement packet's 81 nominal concrete span-stock packages and 486 occurrence IDs. Its first scale-check scenario assumes one trailer trip and one crane rental day per nominal package: `81 × (IQD 1,150,000 + IQD 500,000) = IQD 133,650,000`. Three further trip/day combinations expose sensitivity. These counts are assumptions, not a transport or lift plan; a nominal package is not evidence of one beam, payload fit, crane capacity or one-day erection.

The logistics arithmetic is kept separate from the existing material + direct labour + 20% estimates. The 20% applies only to those declared material and wage subtotals; it is not applied again to the rental observations. Their conditional sums are partial material/labour/logistics subtotals only. Complete delivered/installed cost remains unknown.

### GFRP local fabrication: listed material + local labour + 20%

The current [GFRP cost screen](domestic-fabrication/estimates/current/gfrp-laminate-local-2026-v19.json) joins three 533-record source-bound 10 m² laminate hypotheses to September 2026 CSO governorate skilled-worker base wages and the dated CBI GBP/IQD reference. It retains Baghdad's 9,375 IQD/hour base-wage case and adds 15-governorate 8/16/32 person-hour sensitivities per 10 m². The formula is `(known listed UK material extensions converted at CBI reference + assumed local base-wage labour) × 1.20`.

| 10 m² research recipe | Known listed materials converted to IQD | Partial screen at 8 / 16 / 32 labour hours, including 20% |
|---|---:|---:|
| Solid 600 gsm GFRP | IQD 1,229,647.35 | IQD 1,565,576.82 / 1,655,576.82 / 1,835,576.82 |
| 600 gsm sandwich | IQD 614,823.67 | IQD 827,788.41 / 917,788.41 / 1,097,788.41 |
| Higher-fibre 600 gsm sandwich | IQD 449,362.55 | IQD 629,235.07 / 719,235.07 / 899,235.07 |

The calculator also repeats the same 8/16/32-hour labour sensitivities against all 15 skilled-worker hourly base-wage observations in the September 2026 CSO bulletin. Those construction-worker averages are a proxy for composite-shop labour; employer charges are not included. Kurdistan Region governorates are not represented in that bulletin. Across the listed governorates, the screen ranges are:

| 10 m² research recipe | Regional screen at 8 hours | At 16 hours | At 32 hours |
|---|---:|---:|---:|
| Solid 600 gsm GFRP | IQD 1,535,576.82–1,566,077.22 | IQD 1,595,576.82–1,656,577.62 | IQD 1,715,576.82–1,837,578.42 |
| 600 gsm sandwich | IQD 797,788.41–828,288.81 | IQD 857,788.41–918,789.21 | IQD 977,788.41–1,099,790.01 |
| Higher-fibre 600 gsm sandwich | IQD 599,235.07–629,735.47 | IQD 659,235.07–720,235.87 | IQD 779,235.07–901,236.67 |

These are **partial planning amounts**, not locally sourced composite prices or finished-panel quotes. Easy Composites cloth and resin remain UK listed inputs, and the conversion is a dated non-executable CBI reference. The two sandwich cases have unpriced Corecell M80 and all three cases have unresolved adhesive quantities; their costs remain unknown rather than zero. The scenario also excludes freight, customs, bank charges, mould/tooling, process consumables, scrap beyond the study takeoff, equipment, utilities, employer wage burden, QA, rework, fire/smoke requirements, structural qualification, installation and maintenance. The hours are assumptions, while the 20% allowance is unallocated and does not establish overhead, profit, tax or contingency. Candidate identities, unresolved input IDs and exact source records remain in the machine-readable packet; it cannot rank or select body designs.

An additional [Iraqi retail-material screen](domestic-fabrication/iraq-local-gfrp-retail-screen-2026-10-v1/README.md) records a Mosul seller's public IQD prices for generic fibreglass reinforcement and three resin listings. The seller describes the reinforcement as 300 g/m² and one 1 m² bag at IQD 3,500; it does not publish weave/orientation or a structural grade. The estimate buys 89 bags (89 m², 26.7 kg gross fibre) to cover the 10 m² reference takeoff's 26.67 kg gross fibre mass. It uses eight 300 g/m² plies as a separate mass-equivalent material hypothesis; this does not reproduce the four-ply 600 g/m² biaxial architecture or transfer any analysis result.

At the September 2026 Baghdad CSO skilled-construction-worker base-wage proxy of IQD 9,375/person-hour, the `(listed fabric + assumed direct labour) × 1.20` estimates are IQD **463,800 / 553,800 / 733,800 per 10 m²** for 8/16/32 assumed labour hours. These are fabric-plus-labour partial screens. Resin is excluded from the subtotal because listing chemistry, hardener/catalyst and cure-system compatibility are unknown; the full matrix cost therefore remains unknown, not zero. The retailer asks buyers to reconfirm availability and lead time. The 20% is an unallocated planning uplift on the declared fabric and base-wage labour only; it does not establish employer burden, overhead, profit, tax, freight, tooling, QA or installed cost. Reproduce with `./osr source estimate iraq-local-gfrp --laminate-packet docs/design-engine/sourcing/packets/laminate-materials-iraq-domestic-sources-v18/solid-600gsm --output /tmp/osr-local-gfrp-screen`.

Additional source-only leads include EPS insulation/block products from [Bafra Shakh](https://www.bafrashakh.com/pages/products.php?lang=en) (company-stated 6–30 kg/m³ options, no price or adequate structural allowables in the accessible datasheet) and a [Sama Kirkuk storefront](https://www.sama-kirkuk.com/en/category/construction) with EPS listing labels whose SKU, variant and price unit cannot be resolved. The supplementary set now also includes [REGA aggregate](https://regaasphalt.com/en/page/services-and-products/39/aggregate), whose company page describes three crushing plants and two Erbil rock pits, and [Hewa Trading](https://www.hewa.com/trading), which lists crushed stone, sand and gravel supply as an Iraq-based importer/distributor. These leads do not establish aggregate gradation, test certificates, Iraqi extraction/origin, available quantities, delivery rates, or mix compatibility; September CSO statistics remain the estimate basis, not supplier prices. Neither creates a product offer or concrete-mix approval. The [TC-Safa catalogue](https://tc-safa.com/category/080010000) also lists generic resin at IQD 6,500/kg and Turkish/Iranian-labelled 18 kg cans at IQD 75,000 each; composition, cure package, price validity, freight and compatibility are unresolved, so these observations are retained as leads and are not used to price the laminate matrix. The [Iraq Labour Force Survey 2021](https://www.ilo.org/publications/iraq-labour-force-survey-2021) provides older national employee-earnings context for craft, operator, technician and professional groups; the source rows are not inflation-adjusted and are excluded from current cost estimates.

### Cost/weight sensitivity queue

The unresolved sourcing backlog now accepts candidate-bound `decision_sensitivity` inputs. For explicit ranges, it computes cost and mass scores as `impact-range width × uncertainty fraction × (1 + number of downstream decisions affected)`. It lists alternatives, affected simulations and requested catalogue/supplier evidence beside the score. Safety or design blockers sort ahead of economic results. Cost and mass use separate ranks and Pareto fronts rather than a made-up cost-versus-kilogram exchange rate. A `could_change_preferred` result is produced only when an explicit candidate cost margin and same-currency cost-impact range are present.

No reviewed cost/weight impact ranges or alternatives are declared in the current federated BOM. The controller reports missing inputs for the 137 evaluated unresolved groups; 6,905 other groups remain pending and have not received sensitivity scores. The queue therefore retains the existing system-category order where numeric evidence is absent. It does not claim a numeric expected value of information. The top decision packages that need declarations are the station LIM/converter alternatives, repeated guideway span/foundation, body family/manufacturing route, and complete passive bogie/brake assemblies. Their supplier evidence, quantities, and dependent structural/thermal/motion/civil reruns must be linked to the exact candidate revision before the controller can compare them.

DigiKey's [official Product Information API](https://developer.digikey.com/tutorials-and-resources/oauth-20-2-legged-flow) supports an explicit future catalogue adapter; production pricing requires a registered organization and credentials. No credentials were present during this run, and no price was fabricated. Quotation file parsers likewise produce unverified claims rather than authenticated Class A offers.

## Direct twin runs

The v13 frame and balanced federation price reviews remain bound to their earlier 529-record source epoch: 3,183 of 3,183 frame requirements and 137 of 7,042 federation requirements evaluated, with zero compatible priced matches; 6,905 federation requirements remain pending. Three laminate studies were replayed as v18 against the 533-record source epoch; v16 remains pinned to its earlier source epoch. The current offline catalogue has 533 records and 83 sources. The current v18 procurement package BOM binds that catalogue and ten separate Iraqi discovery records (93 source records total) to the same federation input, and attaches six September 2026 regional/hour estimates and a source-linked ingredient takeoff to each of 81 concrete span packages. It preserves 27,216 located occurrences and the separate 4,773 unlocated obligations. The candidate-bound logistics sensitivity is regenerated as v3 for the same v18 BOM; v2 remains archived. The 2025 and July/September 2026 cost series remain separate dated comparisons. Packet IDs and source record-set identities are in [validation-current.json](validation-current.json). Earlier catalogue epochs remain preserved in their source-bound packets and prior validation indices. Raw downloaded source documents and the SQLite database remain outside the repository.

| Input and purpose | Evaluation | Result |
|---|---|---|
| Full frame-refinement vehicle registry | 3,183 requirement groups; 40,488 physical occurrences; 16 product observations | 0 compatible supplier matches, 0 priced groups, nine disabled RFQ drafts; no complete vehicle or installed cost |
| Federated whole-railway BOM, original occurrence-level packet | 31,989 physical scopes in the historical packet | Its former 137/31,852 budget split predates source-declared manufacturing-group roll-up |
| Federated whole-railway BOM, current manufacturing-group roll-up | 7,042 sourcing requirements cover 31,989 physical scopes: 2,269 manufacturing groups retain 27,216 located occurrences, plus 4,773 unlocated accounts; balanced budget evaluates 137 | 6,905 remain pending; 0 compatible priced groups; all 137 evaluated quantities remain unknown; nine unsent RFQ drafts |
| 10 m² solid GFRP material hypothesis | 4 × 600 g/m² plies, 50% dry-glass fraction, 10% material scrap | 48 kg conditional material screen; GBP 726.65 published extension across cloth and resin lines; no order total |
| 10 m² sandwich GFRP material hypothesis | 2 × 600 g/m² plies plus declared 20 mm Gurit Corecell M80 grade at 85 kg/m³ nominal; 50% dry-glass fraction; 10% scrap | 41 kg nominal; 40.2–41.8 kg bound over the published core-density range; GBP 363.32 listed extension on priced lines; no core price |
| 10 m² higher-fibre sandwich hypothesis | Same named M80 core; two plies; 60% dry-glass fraction; 10% scrap | 37 kg nominal; 36.2–37.8 kg bound over the published core-density range; GBP 265.55 listed extension on priced lines; no core price |

The laminate rows are **new physical research proposals with ancestry to the federated candidate**. Their 10 m² basis is not measured roof CAD area; the core density, fibre fraction and scrap rate are explicit hypotheses. Resin and cloth prices cover only catalogue raw materials. Adhesive, inserts, consumables, labour, mould/tooling, inspection, transport, installation, fire/smoke, hot-wet performance and structural allowables remain unresolved. These figures cannot rank finished vehicle designs or establish a lower-cost railway.

In the current catalogue epoch, the vehicle frame still has 3,183 requirement groups and 0 exact priced matches. The federated manufacturing-group evaluation covers 31,989 physical scopes with 7,042 sourcing groups; the balanced research run evaluated 137 groups and left 6,905 pending. None of the evaluated groups has a compatible priced match, and all 137 evaluated groups still have unknown purchase quantities. The roll-up retains all 27,216 located engineering occurrences under 2,269 source-declared manufacturing groups, while keeping 4,773 unlocated accounts separate. These are practical RFQ scopes, not yet purchasable quantities or costed manufacturing assemblies. Adding Iraqi source data expands the reference library; it does not close the actual railway BOM.

## Reproducible packages

- Retained 305-record source epoch: [vehicle registry](packets/frame-vehicle-iraq-domestic-sources-v6/summary.json) · [federated manufacturing-group roll-up](packets/federated-purchasing-groups-iraq-domestic-sources-v6/summary.json)
- Retained 305-record source epoch: [solid laminate](packets/laminate-materials-iraq-domestic-sources-v6/solid-600gsm/summary.json) · [sandwich laminate](packets/laminate-materials-iraq-domestic-sources-v6/sandwich-600gsm/summary.json) · [higher-fibre sandwich](packets/laminate-materials-iraq-domestic-sources-v6/higher-fibre-sandwich-600gsm/summary.json)
- Retained 307-record source epoch: [solid laminate](packets/laminate-materials-iraq-domestic-sources-v7/solid-600gsm/summary.json) · [sandwich laminate](packets/laminate-materials-iraq-domestic-sources-v7/sandwich-600gsm/summary.json) · [higher-fibre sandwich](packets/laminate-materials-iraq-domestic-sources-v7/higher-fibre-sandwich-600gsm/summary.json)
- Retained 416-record source epoch, v9: [solid laminate](packets/laminate-materials-iraq-domestic-sources-v9/solid-600gsm/summary.json) · [sandwich laminate](packets/laminate-materials-iraq-domestic-sources-v9/sandwich-600gsm/summary.json) · [higher-fibre sandwich](packets/laminate-materials-iraq-domestic-sources-v9/higher-fibre-sandwich-600gsm/summary.json)
- Retained 529-record source epoch: [frame review](packets/frame-vehicle-iraq-domestic-sources-v13/summary.json) · [federated roll-up review](packets/federated-purchasing-groups-iraq-domestic-sources-v13/summary.json)
- Retained priority-capped federation trial: [137 of 7,042 requirements, zero priced matches](packets/federated-purchasing-groups-iraq-domestic-sources-v11-priority-137/summary.json). It uses a single priority-sorted cap and is not comparable with the balanced v13 run.
- Current 533-record laminate studies: [solid](packets/laminate-materials-iraq-domestic-sources-v18/solid-600gsm/summary.json) · [sandwich](packets/laminate-materials-iraq-domestic-sources-v18/sandwich-600gsm/summary.json) · [higher-fibre sandwich](packets/laminate-materials-iraq-domestic-sources-v18/higher-fibre-sandwich-600gsm/summary.json); the v16 studies remain source-bound to 529 records
- [Current Iraqi-labour/imported-material GFRP screen using September 2026 wage observations](domestic-fabrication/estimates/current/gfrp-laminate-local-2026-v19.json)
- [Imported aluminium-stock plus Iraqi labour sensitivity](domestic-fabrication/cso-imported-aluminium-fabrication-sensitivity-2025-2026.json)
- [September 2026 regional materials, wages, concrete and mapped aluminium sensitivities](domestic-fabrication/regional-estimates-2026-september-v6/iraq-domestic-cost-reference-2026-09.json) · [illustrative concrete ingredient recipe](domestic-fabrication/takeoff-recipes/concrete-material-inputs-2026-09.json) · [current v18 candidate procurement package BOM with per-span cost scenarios and ingredient quantities](procurement-bom/federated-v06-research-packages-v18.json.gz)
- Earlier 60-record epoch: [vehicle registry](packets/frame-vehicle/summary.json) · [whole-railway frontier](packets/federated-balanced-frontier/summary.json) · [manufacturing-group roll-up](packets/federated-purchasing-groups/summary.json)
- Prior 98-record, pre-sensitivity epoch: [validation index](validation-domestic-iraq-pre-sensitivity.json) · [vehicle registry](packets/frame-vehicle-iraq-sources-pre-sensitivity-controller/summary.json) · [federated roll-up](packets/federated-purchasing-groups-iraq-sources-pre-sensitivity-controller/summary.json)
- Earlier 60-record epoch: [solid laminate](packets/laminate-solid-600gsm/summary.json) · [sandwich laminate](packets/laminate-sandwich-600gsm/summary.json) · [higher-fibre sandwich](packets/laminate-higher-fibre-sandwich-600gsm/summary.json)
- Domestic fabrication: [4-hour rebar](domestic-fabrication/estimates/current/rebar-cut-bend-04h-v6.json) · [8-hour rebar](domestic-fabrication/estimates/current/rebar-cut-bend-08h-v6.json) · [16-hour rebar](domestic-fabrication/estimates/current/rebar-cut-bend-16h-v6.json)
- Concrete batch screens: [2-hour](domestic-fabrication/estimates/current/concrete-batch-02h-v6.json) · [4-hour](domestic-fabrication/estimates/current/concrete-batch-04h-v6.json) · [8-hour](domestic-fabrication/estimates/current/concrete-batch-08h-v6.json) · mapped [Baghdad 2/4/8-hour cases](domestic-fabrication/estimates/current/concrete-takeoff-02h-v6.json)
- [Current source epoch and packet index](validation-current.json) · [retained prior source-bound run index](validation.json)

From a repository checkout:

```bash
./osr source init
./osr source seed
./osr source refresh
./osr source run \
  --input docs/design-engine/frame-refinement/packet \
  --as-of 2026-10-30 --target-currency GBP \
  --output /tmp/osr-frame-sourcing-review
./osr source verify /tmp/osr-frame-sourcing-review
./osr source study laminate \
  --input docs/design-engine/sourcing/packets/federated-purchasing-groups-iraq-domestic-sources-v13/input.json.gz \
  --as-of 2026-10-30 --target-currency GBP \
  --output /tmp/osr-laminate-studies
./osr source verify /tmp/osr-laminate-studies/solid-600gsm
./osr source estimate fabrication \
  --input docs/design-engine/sourcing/packets/federated-purchasing-groups-iraq-domestic-sources-v13/input.json.gz \
  --recipe docs/design-engine/sourcing/domestic-fabrication/recipes/rebar-cut-bend-08h.json \
  --output /tmp/osr-domestic-fabrication-estimate.json
./osr source estimate gfrp-laminate \
  --packet-root docs/design-engine/sourcing/packets/laminate-materials-iraq-domestic-sources-v18 \
  --output /tmp/osr-gfrp-local-fabrication-screen.json
./osr source procurement-bom \
  --input docs/design-engine/sourcing/packets/federated-purchasing-groups-iraq-domestic-sources-v6/input.json.gz \
  --regional-cost-reference docs/design-engine/sourcing/domestic-fabrication/regional-estimates-2026-september-v6/iraq-domestic-cost-reference-2026-09.json \
  --concrete-material-recipe docs/design-engine/sourcing/domestic-fabrication/takeoff-recipes/concrete-material-inputs-2026-09.json \
  --output /tmp/osr-procurement-bom-2026-september.json.gz
./osr source estimate iraq-logistics \
  --procurement-bom docs/design-engine/sourcing/procurement-bom/federated-v06-research-packages-v18.json.gz \
  --regional-cost-reference docs/design-engine/sourcing/domestic-fabrication/regional-estimates-2026-september-v6/iraq-domestic-cost-reference-2026-09.json \
  --output /tmp/osr-iraq-span-logistics
./tools/automation/osr-python -m engineering.sourcing.iraq_import_fabrication_scenarios \
  --output /tmp/osr-imported-aluminium-fabrication-sensitivity.json
./tools/automation/osr-python -m engineering.sourcing.current_validation
./osr source serve
```

The SQLite database defaults to the user's XDG state directory, outside the checkout. Raw feed bytes default to the user's XDG data directory; the scheduled CI job retains only JSON status artifacts, not feed files or credentials. The Workbench binds to `127.0.0.1:8774`, uses paginated projections and denies every HTTP write method. RFQ drafts remain disabled; no supplier is contacted and no ERPNext production record or active manufacturing order is changed.

## Remaining closure work

The next high-value data is exact source-bound product mappings and supplier RFQs for the actual station-LIM winding/converter, complete passive bogie, independent brake, HVAC at Baghdad design temperature, doors/glazing, and precast guideway/foundation assemblies. The source database can retain the evidence, produce a draft request package, and invalidate dependent evaluations when an approved proposal changes. It cannot make missing geometry, source documents, supplier replies, Iraqi installed rates or physical test data appear. The whole-cell run has **zero exact priced matches**, and complete installed/whole-life cost, physical qualification and an integrated selected railway remain `unknown`.
