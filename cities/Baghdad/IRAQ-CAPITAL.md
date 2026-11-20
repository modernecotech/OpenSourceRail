# What the Baghdad networks could cost to build

An Iraqi buyer can carry **about $8.37bn for the first network** and **$33.00bn for the metropolitan alternative** in constant 2026 money. The uncertainty is wide enough to matter to a financing decision. On the first network alone, the complete fleet, civil works and stations account for over two thirds of the central direct estimate. The table sets each independent option beside the common engineering price used to compare bidder returns. It uses the cost plan's 1,510 IQD/USD translation. [Common engineering price](COST-AND-DELIVERY.md) · [Currency assumption](iraq-market.toml)

<!-- Iraq capital tables -->

| Independent network | Common bid control $bn | Iraq installed $bn, low / base / high | IQD trillion, low / base / high | Base Iraqi award / domestic value within award $bn |
|---|---:|---:|---:|---:|
| First | 7.866 | 6.122 / 8.369 / 12.350 | 9.24 / 12.64 / 18.65 | 3.363 / 1.842 |
| Metropolitan | 31.018 | 24.097 / 32.995 / 48.828 | 36.39 / 49.82 / 73.73 | 13.319 / 7.363 |

| Matched package | First $m, low / base / high | Metropolitan $m, low / base / high |
|---|---:|---:|
| Elevated civil works | 902.4 / 1,343.3 / 2,276.1 | 3,688.3 / 5,490.3 / 9,302.8 |
| Stations and access | 614.4 / 883.2 / 1,312.0 | 2,688.0 / 3,864.0 / 5,740.0 |
| Track and walkways | 198.7 / 265.9 / 366.8 | 812.0 / 1,086.8 / 1,499.0 |
| Signalling and communications | 133.4 / 200.1 / 296.4 | 545.1 / 817.6 / 1,211.3 |
| Brake protection and recovery | 66.7 / 96.3 / 140.8 | 272.5 / 393.7 / 575.4 |
| Line traction supply | 253.5 / 339.1 / 459.5 | 1,038.8 / 1,389.4 / 1,882.8 |
| Grid supply sites | 159.4 / 240.3 / 334.2 | 531.4 / 801.0 / 1,114.0 |
| Complete trains | 1,856.4 / 2,227.7 / 2,877.4 | 7,164.8 / 8,597.8 / 11,105.5 |
| Depots and control centres | 196.0 / 284.0 / 416.0 | 560.0 / 808.0 / 1,184.0 |
| Land, utilities and disruption | 161.5 / 323.0 / 673.0 | 660.1 / 1,320.2 / 2,750.4 |
| Tooling and recovery | 74.5 / 108.7 / 161.3 | 211.7 / 314.5 / 458.7 |
| Design and assurance | 369.4 / 504.9 / 745.1 | 1,453.8 / 1,990.7 / 2,945.9 |
| Testing and commissioning | 115.4 / 157.8 / 232.8 | 454.3 / 622.1 / 920.6 |
| Project contingency | 1,020.3 / 1,394.9 / 2,058.3 | 4,016.2 / 5,499.2 / 8,138.1 |

<!-- end Iraq capital tables -->

### What the budget buys

The first network prices 148.2 route-km, 296.4 track-km, 29,640 beam placements, 29,654 support and foundation positions, 64 station allowances, 242 six-car trains, 30 grid sites, four depots and two control centres. The metropolitan alternative prices 605.652 route-km including the 50.099 km passenger-service reserve, 280 station allowances, 934 trainsets, 100 grid sites, twelve depots and four control centres. Counts come from the selected protected-conductor railway. The cash schedule spreads each case over the dates and weights of its own programme. [Selected quantities and schedule](system-results.json)

The total adds 8% of direct packages for programme design and assurance and 2.5% for integrated testing. The 20% project allowance applies once to their combined subtotal. The low and high columns vary direct procurement and works rates together, representing favourable and adverse purchasing and construction conditions. All three columns retain the same contingency policy and railway scope. They are planning scenarios. Taxes, borrowing, escalation after 2026, and subsequent operations and renewals are separate. [Cost assumptions](system.toml) · [Local rates](iraq-capital.toml)

The Iraqi award and retained-value figures apply the existing work-package percentages to the repriced **base case only**, excluding contingency. Award shares transfer from metropolitan to the first network on the same basis as the buyer guide. The dollar amounts in the buyer guide continue to use the original common bid control. The new market price adds no localisation premium or saving. Central awards and domestic value by package are available in the calculation output. [Buyer comparison and retention assumptions](BUYER-COMPARISON.md) · [Produce the figures](iraq_capital.py)

### Why the rates differ

| Purchasing package | Basis for Iraq allowance |
|---|---|
| Beams, supports and erection | Use October 2026 Iraqi cement, reinforcing steel, sand and crushed gravel prices. Budget 0.39 t cement, 0.45 m³ sand, 0.80 m³ gravel and 0.10 / 0.14 / 0.19 t reinforcing steel per finished m³ as a pricing recipe. Use the straight-bay quotation study's 13.404 m³ per beam and 14.406 m³ per support as representative quantities. The base dry materials are $155/m³. Each beam also carries $8,000 / $11,500 / $16,500 for conversion, prestressing supplies, mould use, curing, QA, bearings and ordinary haul. Each support adds $3,600 / $6,500 / $14,000 for excavation, placing, temporary works and local ground treatment. Each lift adds $3,300 / $5,000 / $8,500. These are tender allowances. |
| Remaining elevated works | $2.4m / $3.6m / $6.5m per route-km covers drainage, longitudinal details, temporary access, yard/front preparation and variable construction conditions beyond the separately priced articles. The central figure approximates the existing $9m/km allowance less its priced beams, piers and lifts. Boundary work and ordinary traffic access during erection sit here. Land acquisition and permanent utility relocation sit in the land account. |
| Stations | $9.6m / $13.8m / $20.5m per budgeted accessible station. Civil works and finishes take $6m / $8m / $11.5m, station equipment and vertical circulation $2.5m / $3.8m / $5.5m, and street access and egress structures $1.1m / $2m / $3.5m. The division follows tenderable boundaries. India's metro benchmark separately lists civil/finishes and electromechanical equipment at 26 and 8 crore rupees per elevated station and excludes route viaduct from the station. Baghdad's amounts are buyer allowances for imported equipment and local works. Each price covers one complete budget slot. |
| Trains | Alstom's November 2022 Chennai order was €98m for 78 driverless cars including design, manufacture, supply, testing, commissioning and training. At the November 10 USD/EUR rate of 1.0176 the six-car equivalent was $7.67m. Apply 1.00 / 1.20 / 1.55 for price date, import logistics, summer duty, adaptation, spares and warranty, yielding $7.67m / $9.21m / $11.89m per Baghdad train. A large repeat order drives the low case. Chennai used three-car formations. Linear scaling by car is a commercial comparison pending a six-car Baghdad offer. Programme integration and central assurance exclude supplier-internal design and factory test already in purchase prices. |
| Track and walkways | The Iraqi Republic Railways project appraisal gives $33m for 32 km of brownfield renewal on the Al Yussufia–Baghdad section. Apply 0.65 / 0.87 / 1.20 of that numeric rate per elevated track-km, giving $0.67m / $0.90m / $1.24m for rails, fasteners, walkways and installation. The guideway is already priced. The source has different trackform, logistics and works boundaries. These factors expose the transfer assumption. |
| Land, utilities and disruption | The Ministry of Planning reports about IQD 96bn for seven km of the Baghdad–Wasit approach road including bridges, service roads and diversions. It records interference with power, water and commercial premises. As a broad urban-corridor cost reference we divide that published nominal amount by seven, translate at the plan rate and allow 12% / 24% / 50% per railway route-km for parcels, utility diversions, traffic and reinstatement. These assumed shares give $1.09m / $2.18m / $4.54m per km. They require replacement with a parcel and utility register. |
| Rail systems | Allow $0.90m / $1.35m / $2.00m per route-km for signalling and communications and $0.45m / $0.65m / $0.95m for wayside brake protection and rescue. Iraq's national railway project estimates $570m for signalling and fibre ducts along 1,047 km of existing railway. The metro allowances provide for denser control, passenger protection and redundancy. Price the existing conductor quantities and section switches at 0.80 / 1.07 / 1.45 times their engineering unit allowances to cover imported assemblies, local installation and testing. Each grid site separately receives the complete Iraqi traction-site estimate. |
| Depots, control and tooling | Allow $42m / $60m / $88m per new depot and $14m / $22m / $32m per control centre, including buildings and fixed equipment. Iraq's $10m Baiji workshop refurbishment and maintenance-equipment package helps identify the workshop equipment portion. New depots also require stabling, inspection, lifts, buildings and services. Tooling and recovery across both vehicle and wayside works use $30m / $42m / $65m fixed plus $0.30m / $0.45m / $0.65m per route-km. These estimates cover tooling and vehicles outside the unit rates. |

The raw-material entries come from Iraq's October 2026 official construction-material tables. The straight-bay volume study is a pricing proxy with its own design identity. Selected train and civil quantities stay as published. Rebar and manufacturing allowances do not qualify the beam, lifting points or footing. Geotechnical improvement and major river or motorway crossings can exceed these scenarios. The airport project's extra piles, crossings, airport terminal works, depot lead and special haul quantities have no network-wide multiplier. Replace the general allowances with separately surveyed and matched lots as alignments and site returns become available. [Iraqi material data and references](airport-works.toml) · [Trial section and excavation limits](engineering/mechanical/civil/README.md) · [Baghdad–Wasit works](https://mop.gov.iq/archives/10965)

The rail comparison uses project estimates from Iraq and a signed international train contract. Prices and scope differences are visible in the underlying reports. Firm priced returns from Iraqi contractors and equipment manufacturers can displace one matched scope at a time. [World Bank Iraqi rail project, table 1](https://documents1.worldbank.org/curated/en/099050425130516662/pdf/P507282-091efafd-26a7-46f4-86ce-5b25f875478b.pdf) · [Alstom train order](https://www.alstom.com/sites/alstom.com/files/2022/11/10/20221111_PR_Metro_Coaches_for_Chennai_Metro_PhaseII_EN.pdf) · [Federal Reserve November 2022 exchange rates](https://www.federalreserve.gov/releases/h10/20221114/) · [Indian metro cost benchmark](https://www.mohua.gov.in/upload/whatsnew/5c6bdd5429cd4Report%20on%20Benchmarking%20for%20Cost%20Estimation%20of%20Metro%20Rail%20Projects-.pdf) · [Iraqi grid-site procurement and price evidence](IRAQ-POWER.md)
