# OpenSourceRail Baghdad metropolitan railway

**Proposal to Amanat Baghdad · 18 November 2026 · planning prices in 2026 US dollars**

## Brief

Baghdad needs a railway that serves daily trips across the city, reaches the airport passenger terminal, and can grow with its population. OpenSourceRail proposes a locally buildable, repairable electric railway on standardised elevated structures. The passenger lines have **no tunnels or underground stations**. Trains draw power from a protected conductor beside the track, so the preferred design has **no overhead wires**. Iraqi factories and contractors would take an increasing share of precast concrete, vehicle bodies, stations, assembly and maintenance.

The proposal offers **two independent choices**. The **148.2 km concept** follows the seven corridors named in the Iraqi investment brief. The **605.652 km citywide concept** starts from its own nine cross-city and ring corridors, six infill corridors and through-service connections. It is planned as a complete network for Baghdad in 2035; its route, fleet, station and capital totals do not inherit the 148.2 km concept. Geographic crossings may be useful interchange locations, but neither map is a construction stage of the other. Short access branches belong to through trains, with no separate shuttle fleet.

| Programme | Railway | Stations budgeted | Train fleet | Construction capital | Target completion |
|---|---:|---:|---:|---:|---:|
| Seven-corridor concept | 148.2 km | 64 | 242 six-car trains | **US$7.866bn** | 2031 |
| Independent citywide concept | 605.652 km | 280 | 934 six-car trains | **US$31.018bn** | 2035 |

These are **one estimate for each alternative**, each priced as a complete railway. They must not be added or subtracted to describe a build sequence. The detailed [cost and delivery schedule](COST-AND-DELIVERY.md) names every quantity, rate, annual operating cost and renewal.

## The city and the routes

The [seven-line first-programme map](maps/Baghdad-148km.png) uses the [Iraqi National Investment Commission's 2024 Baghdad Metro route brief](https://investpromo.gov.iq/wp-content/uploads/2024/03/3.-RFI-English-%D9%86%D8%A8%D8%B0%D8%A9-%D8%B9%D9%86-%D9%85%D8%AA%D8%B1%D9%88-%D8%A8%D8%BA%D8%AF%D8%A7%D8%AF-E-20.2.2024.pdf) for line names, lengths and the 64-station programme. Both maps show streets, the Tigris, land use and place names from the existing Baghdad city background beneath the railway. Its named squares and districts are placed using OpenStreetMap where a usable public feature exists. The lines show corridor intent. A district centroid is a place marker, not an approved station entrance.

| Line | Length | Principal places served |
|---|---:|---|
| Green | 19 km | Al Alawi, Mansour, Yarmouk, Bayaa, Doura |
| Red | 27.7 km | Al Alawi, Kadhimiya, Adhamiya, Mustansiriya, Maisaloun |
| Blue | 22 km | Al Shaab, Waziriya, Khallani, Tayaran, Zuafaraniya |
| Purple | 14.5 km | Tayaran, Hamza, Ur, Al Shaab and Sadr City approaches |
| Yellow | 30 km | Baladiyat, Maisaloun, Chadriya/Jadriya, Bayaa, Adan |
| White | 23 km | Kadhimiya, Shulah, Gazaliya, Khadhraa, Amiriya, Bayaa |
| Airport | 12 km | Airport passenger-terminal area, Amiriya, Aamil, Bayaa, Qadisiya |

**Airport service** is part of the railway, not a feeder bus assumption. The Airport line's western end is mapped to the passenger-terminal building area. The station must connect to the landside entrance by a step-free, protected walking route, with the operating and security boundary agreed with the airport. The public map locates the terminal building, not its final station platform.

The independent citywide network gives the **airport terminal** an access section on service M05; it assigns the three **Sadr City** anchors to M04 and M09 through branches and the two **Jadriya** anchors to M01 and M02. The Sadr cross-city services M10 and M11 and the southwest service M13 add direct capacity through those catchments. These are schematic railway corridors to the named access areas, not approved platform sites or walking routes.

The [citywide map](maps/Baghdad-606km.png) contains 26 schematic physical sections: nine principal corridors, five shared links, six infill corridors and six access branches. All are included in the citywide route-length control. The **14 named service groups** cover 20 sections; the other six have a stated planning purpose but no train path. The station budget is 280. The two maps' lengths are declared planning controls; their drawn polylines are not measured construction centre lines. The [map guide](maps/README.md) provides the editable GIS layers and sources.

| Through-service groups | Citywide role |
|---|---|
| M01–M03 | Cross-city spines; M01 reaches Jadriya west, M02 reaches Jadriya east |
| M04–M06 | Northwest–southeast and east–west spines; M04 reaches Sadr south and centre, M05 reaches the airport terminal |
| M07–M09 | East–west, southeast–northwest and orbital services; M09 reaches Sadr east |
| M10–M11 | Sadr City east–west and north–south services |
| M12–M14 | Karkh north–south, southwest cross-city and northern cross-city services |

The route IDs and their physical sections are in [the network input](system.toml) and [GIS layer](maps/network-606km.geojson). The 14 named service groups cover 20 of the 26 costed citywide sections. Five shared connectors and the east inner arc total 50.099 km of normalized guideway and have no assigned train path. They are counted once in the civil and power budget; their operation is excluded from the current service allowance.

## Trains and passenger service

The Baghdad train has **six 17 m cars**, a coupled length of about 104.5 m and a **125 m clear platform**. Each car has four 1.3 m clear double-leaf door openings on each side, 20 fixed seats and two wheelchair places. The train carries about **700 people** at its normal urban-service cap, including planned standing. Step-free access, platform gaps, evacuation width and independent stopping are design duties, not cost-saving options.

Powered wheel bogies give the train sustained traction between stations. The protected conductor design has **24 driven axles**, a **201.092 t** crowd-load train mass and a **5.004 MW** input sizing request at the stated uphill acceleration duty. It does not carry a traction battery or a roof collector. Each train's independent 65 kWh nominal service battery supplies controls, lighting, braking and egress duty for the declared two-hour outage case; its mass, recharge power and price are included in the existing train allowances. Baghdad summer cooling is included in the vehicle and energy allowances. The [vehicle and station section](VEHICLE.md) gives the car layout, platform gap, protected conductor position and replacement interfaces.

A **150-second peak interval** offers **16,800 places per hour per direction on one service**. The seven-corridor alternative budgets **210 active trains and 242 with reserve**; the independent citywide alternative budgets **812 active and 934 total** for 14 service groups. Applying that peak interval for every hour gives about **4.234 million nominal places per day** across the seven corridors in both directions; this is a capacity allowance, not a timetable or ridership forecast. The 38 km/h commercial-speed and 18-hour utilisation allowances give **52.429 million train-km/year** for the seven-corridor alternative and **202.724 million** for the citywide alternative.

## Viaducts, stations and street works

Both tracks are costed on an elevated alignment for every revenue route kilometre. The construction family uses **10 m precast beams**, separate support and foundation positions for each track, rail fastenings, drainage and a maintenance and evacuation walkway. Repetition permits local casting yards, straightforward transport and replacement. The seven-corridor alternative counts **29,640 beam placements and 29,654 support positions**; the independent citywide network counts **121,156 beams and 121,208 positions**. The planning lift mass is **37.3 t per beam**, subject to an actual crane and handling design.

Accessible stations provide clear passenger routes, lifts or ramps where required, protected platform edges, fire and evacuation provisions, equipment access and safe transfer to streets and buses. A station's structural and electrical modules should be replaceable without redesigning the whole line. The capital estimate counts **64 stations** first and **280** for the independent citywide network, at a common planning rate of **US$13m each**.

Longer 20, 25 and 30 m spans could reduce foundation counts in constrained streets. Their indicative whole-system prices are shown in the [civil comparison](COST-AND-DELIVERY.md#viaduct-and-construction). They require heavier lifts and their own structural and erection design, so the 10 m family remains the costed construction reference. Road clearances, river crossings, existing utilities and actual foundation ground are site-specific work and are not invented in the map.

## Power, operations and maintenance

Protected conductor rail gives each train power throughout its journey without continuous overhead equipment or a large traction battery. The budget counts **296.4 track-km** of guarded conductor and **30 grid sites** in the seven-corridor alternative; the independent citywide network counts **1,211.304 track-km** and **100 grid sites**. Section switches, isolation, return current, touch protection, maintenance access and emergency evacuation are part of the installation scope. The two grid design requests are about **254 MW** and **984 MW** respectively; annual delivered energy is **1,114 GWh** and **4,309 GWh** under each alternative's service assumptions.

A 30-year comparison holds the passenger service constant while changing the train mass, batteries, grid, guideway equipment, electricity use, maintenance and renewals. Under the stated prices, protected conductor has the lowest total cost. The difference from overhead supply is small enough that actual procurement prices can change the choice; the comparison must be rerun before a supply contract is awarded.

| Power supply | First capital | First 30-year cost | Complete capital | Complete 30-year cost |
|---|---:|---:|---:|---:|
| **Protected conductor, preferred** | **$7.866bn** | **$14.493bn** | **$31.018bn** | **$57.214bn** |
| Station-charged battery | $8.201bn | $15.238bn | $32.169bn | $59.832bn |
| Short powered sections plus battery | $7.828bn | $14.612bn | $30.923bn | $57.679bn |
| Overhead supply comparison | $7.927bn | $14.560bn | $31.262bn | $57.473bn |

The selected seven-corridor railway budgets **US$339.974m/year** for electricity, trains, stations and power-system upkeep. The independent citywide railway budgets **US$1,348.404m/year** at full service. The 30-year present costs include those running costs and scheduled equipment and fleet renewal at a **4% real discount rate**. Fare income, public service payments, debt interest and tax are separate financial decisions.

## Iraqi factories and supply chain

Each alternative should buy repeatable assemblies through open drawings and inspectable specifications. The five-year seven-corridor plan needs **three beam-casting yards and three erection fronts** at the modelled eight beams or lifts per workday per yard or front. The independent citywide plan needs **seven of each** across its nine-year programme. These are production-capacity allowances within each alternative, not shared or already appointed factories.

| Work package | Intended Iraqi contribution | Procured or specialist input |
|---|---|---|
| Viaduct and foundations | Precast beams, piers, reinforcement cages, concrete, erection and repair | Bearings, stressing equipment and specialist testing where needed |
| Train cars | Carbody fabrication, doors and interiors, cable looms, final assembly and depot repair | Motors, converters, bearings and safety-critical controls initially |
| Stations | Structures, stairs, lifts installation, fit-out and passenger facilities | Certified equipment, fire and control components |
| Electrical railway | Cable routes, cabinets, installation, protection enclosures and routine maintenance | Contact equipment, switchgear and traction substations initially |
| Operations | Local staff, training, inspection, spares stores and renewal works | Initial specialist commissioning and training support |

The seven-corridor capital estimate includes **US$99.280m** for tooling, rescue and local-production setup; the independent citywide estimate includes **US$282.261m**. At the declared planning shares by contract scope, **US$12.599bn** of the citywide **US$25.848bn** non-contingency capital is addressable by Iraqi labour, materials, factories and engineering. This is a procurement target and contract-value opportunity, not an assertion that those orders have been placed or a deduction from the **US$31.018bn** total. The [scope-by-scope calculation](COST-AND-DELIVERY.md#local-production-and-design-rights) lets the city compare tender returns with the target.

The Iraqi public design custodian and participating manufacturers should receive the editable drawings, CAD, BOMs, control source, tooling files, inspection methods and revision history needed to **make, modify, repair and re-procure** the railway. The tender should require newly funded design work to be delivered under the applicable [OpenSourceRail licences](../../LICENSE.md) or separately assigned to the Iraqi public sponsor, and identify any supplier background rights, royalties and locked interfaces. Existing third-party map and component rights stay separately recorded. No hypothetical royalty saving is deducted from capital or operations; a bidder's priced alternative can expose that saving.

## Capital, construction cash and delivery

The **US$7.866bn** seven-corridor estimate and the **US$31.018bn** independent citywide estimate each cover viaducts, stations, track, signalling, protection, power, trains, depots, land and utilities, tooling, design, commissioning and one 20% project allowance. Neither is an increment to the other. The [fourteen-scope ledger](COST-AND-DELIVERY.md#fourteen-installed-capital-scopes) reconciles each estimate separately.

The seven-corridor alternative is planned for **2027–2031**. The citywide alternative has its own **2027–2035** construction sequence, with coordinated rights, utilities, factories, parallel civil works, train production and staged openings. The annual construction cash requirement for either choice is:

| Year | Seven-corridor alternative | Independent citywide alternative |
|---|---:|---:|
| 2027 | $393m | $931m |
| 2028 | $1,180m | $2,171m |
| 2029 | $2,360m | $3,102m |
| 2030 | $2,360m | $4,032m |
| 2031 | $1,573m | $4,653m |
| 2032 | — | $5,273m |
| 2033 | — | $4,653m |
| 2034 | — | $3,722m |
| 2035 | — | $2,481m |
| **Total** | **$7,866m** | **$31,018m** |

Each column is a standalone funding requirement and is rounded from the [annual cash schedule](COST-AND-DELIVERY.md#annual-construction-capital-draw). Debt interest, export-credit premiums and operating support are outside these construction totals.

## Raising the capital

Amanat Baghdad and the relevant Iraqi authorities would first settle the sponsoring and borrowing entity, procurement rights, land access, operating model and government support. The first financing package can then be tendered in separate civil, vehicle, power, signalling and depot contracts against the same network quantities. Iraqi public capital can fund land, locally procured civil works, buyer cash contributions and the project reserve. Commercial banks can consider construction loans or longer-term debt once the contracts, completion support and repayment source are agreed.

[UK Export Finance's Buyer Credit Facility](https://www.gov.uk/guidance/buyer-credit-facility) can guarantee an acceptable bank's loan to an overseas public or private buyer for an eligible UK export contract. The UK exporter must be carrying on business in the UK, the contract must be worth at least **£5m**, and repayment must run for at least two years. The facility can cover **up to 85% of that export contract**, with at least **15% paid directly by the buyer**. This is a contract rule, not an 85% financing assumption for the Baghdad network. [UKEF's content policy](https://www.gov.uk/government/publications/ukefs-approach-to-foreign-content/ukefs-approach-to-foreign-content) and environmental, social, human-rights, integrity and country-cover checks also apply.

UK export opportunities include engineering services, traction and control equipment, station systems, train components and training. Iraqi casting, civil works and assembly remain separately priced contracts unless an eligible export package includes them. Bank and UKEF amounts depend on contracts and a repayment plan. **No unapproved loan is counted as raised capital.**

## Decision requested

Amanat Baghdad is asked to compare the two **independent** networks on coverage, capacity, installed and whole-life cost, local contract value and design rights. The citywide choice should safeguard through service to the airport, Sadr City and Jadriya and procure connected route, station, factory, power and finance packages. Tender returns should price local manufacturing, repair, training and transferable design deliverables against the same service specification.

**Basis of this proposal:** the published Iraqi route brief, open GIS place and population layers, the [Baghdad maps](maps/README.md), the [train](VEHICLE.md) and the [integrated cost schedule](COST-AND-DELIVERY.md). The maps and figures support a funding and procurement discussion. They do not claim surveyed alignments, supplier bids or operating approval.
