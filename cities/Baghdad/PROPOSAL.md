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

## Earlier idea and present planning design

OpenSourceRail began with a light, wheel-supported train accelerated at stations, then coasting between them. That remains a useful cost-reduction question. The Baghdad planning design uses motors on the train and a protected conductor alongside the rail because its longer, graded journeys need sustained traction. Both ideas retain open design, local fabrication, accessible stations and independent braking. They are distinct physical candidates: the powered Baghdad train's fleet price and energy cannot be assigned to a passive train.

| Design decision | Station-launch, passive-wheel idea | Present Baghdad planning design |
|---|---|---|
| Train propulsion | Station equipment provides launch force; train coasts between stations | Wheel motors provide launch, acceleration and hill-climbing throughout the trip |
| Line power | Local launch equipment and service power; powered length depends on each stop | Guarded, sectionalised conductor on both tracks; no overhead wires |
| Train equipment | Passive bogies, independent service battery and brakes | 24 driven axles, converters and contact shoes; separate 65 kWh service battery and brakes |
| Civil and stations | Track, launch/braking equipment, power and interfaces sized for the selected route | Elevated double track, wayside protection, grid sites and accessible stations |
| Cost and status | Research option; no matched Baghdad installed cost or service timetable | Integrated 148.2 km and independent 605.652 km planning estimates below |

The earlier coast calculation cannot carry a crowded train through every long or uphill Baghdad section at the desired speed. A cheaper station-launch design would need a route-specific mix of shorter gaps, booster sections or small onboard motors and storage, plus a full stopping and recovery case. The **station-charged battery** row later in this proposal is a *powered-bogie train*, not that passive station-launch idea. It must not be presented as its cost.

The present plan also changes the older tunnel and overhead assumptions: **zero passenger tunnels and zero underground stations** are fixed planning requirements, while the conductor is the lowest priced supply under the current assumptions, not a supplier-proven winner. A no-catenary system remains the preferred procurement outcome. A tender can test overhead, limited-conductor and battery alternatives against identical service, safety and 30-year cost duties.

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

### What the maps establish

The seven-corridor lines draw 138.395 km against the investment brief's 148.2 km route-length control. The citywide linework draws 608.460 km and is normalized to a 605.652 km cost control. The first map has named districts and access markers, not 64 approved station points; the citywide stop screen has 220 points against a 280-station budget. A detailed station register therefore has to assign the balance and connect every funded section to a train path before a binding timetable or location-specific land budget is used. The six unassigned citywide sections are labelled in the map source and should receive a named passenger, connector or depot function at route design stage.

The GIS background and district names are useful for public discussion, utility searches and corridor screening. Open imagery cannot resolve bridge clearances, foundation ground, actual property rights or platform entrances. The cost estimate uses allowances for those items rather than treating them as free.

## Trains and passenger service

The Baghdad train has **six 17 m cars**, a coupled length of about 104.5 m and a **125 m clear platform**. Each car has four 1.3 m clear double-leaf door openings on each side, 20 fixed seats and two wheelchair places. The train carries about **700 people** at its normal urban-service cap, including planned standing. Step-free access, platform gaps, evacuation width and independent stopping are design duties, not cost-saving options.

Powered wheel bogies give the train sustained traction between stations. The protected conductor design has **24 driven axles**, a **201.092 t** crowd-load train mass and a **5.004 MW** input sizing request at the stated uphill acceleration duty. It does not carry a traction battery or a roof collector. Each train's independent 65 kWh nominal service battery supplies controls, lighting, braking and egress duty for the declared two-hour outage case; its mass, recharge power and price are included in the existing train allowances. Baghdad summer cooling is included in the vehicle and energy allowances. The [vehicle and station section](VEHICLE.md) gives the car layout, platform gap, protected conductor position and replacement interfaces.

A **150-second peak interval** offers **16,800 places per hour per direction on one service**. The seven-corridor alternative budgets **210 active trains and 242 with reserve**; the independent citywide alternative budgets **812 active and 934 total** for 14 service groups. Applying that peak interval for every hour gives about **4.234 million nominal places per day** across the seven corridors in both directions; this is a capacity allowance, not a timetable or ridership forecast. The 38 km/h commercial-speed and 18-hour utilisation allowances give **52.429 million train-km/year** for the seven-corridor alternative and **202.724 million** for the citywide alternative.

The passenger offer includes step-free entry, wheelchair spaces, clear door signs, audible and visible next-stop information, Arabic and English wayfinding, line maps, disruption displays and staffed assistance. Station equipment needs a local information feed so a power or communications interruption cannot silently leave misleading departure or evacuation messages. Platform crowd handling, transfer walking distances and actual peak/off-peak frequency require an hourly service plan; no daily ridership or fare revenue is assumed in the financial totals.

## Viaducts, stations and street works

Both tracks are costed on an elevated alignment for every revenue route kilometre. The construction family uses **10 m precast beams**, separate support and foundation positions for each track, rail fastenings, drainage and a maintenance and evacuation walkway. Repetition permits local casting yards, straightforward transport and replacement. The seven-corridor alternative counts **29,640 beam placements and 29,654 support positions**; the independent citywide network counts **121,156 beams and 121,208 positions**. The planning lift mass is **37.3 t per beam**, subject to an actual crane and handling design.

Accessible stations provide clear passenger routes, lifts or ramps where required, protected platform edges, fire and evacuation provisions, equipment access and safe transfer to streets and buses. A station's structural and electrical modules should be replaceable without redesigning the whole line. The capital estimate counts **64 stations** first and **280** for the independent citywide network, at a common planning rate of **US$13m each**.

Longer 20, 25 and 30 m spans could reduce foundation counts in constrained streets. Their indicative whole-system prices are shown in the [civil comparison](COST-AND-DELIVERY.md#viaduct-and-construction). They require heavier lifts and their own structural and erection design, so the 10 m family remains the costed construction reference. Road clearances, river crossings, existing utilities and actual foundation ground are site-specific work and are not invented in the map.

The factory sequence for each repeatable span is mould and reinforcement preparation, cast and cure, dimensional and material inspection, yard release, protected transport, support and bearing inspection, lift and temporary restraint, permanent connection, track fixing and final inspection. The estimate includes beam, support and installation allowances. Crane radius, temporary works, river crossings and working-hour restrictions must be priced in corridor contracts before a construction schedule is committed. At eight placements per working day and 250 working days per year, the stated 2028–2030 civil window needs **at least five casting yards and five erection fronts** for the 148.2 km option; 2028–2034 needs **at least nine of each** for citywide delivery. These are minimum throughput counts with little disruption margin, not commissioned factories.

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

The conductor-versus-overhead 30-year advantage is **$66.644m** on the seven-corridor network and **$259.323m** citywide, about **0.46%** of the total in each case. An increase of about **$0.158m** or **$0.151m per track-km** respectively in conductor equipment cost removes that advantage if other assumptions stay fixed. Procurement should therefore request both systems' installed prices, losses, renewals, access requirements and maintenance staffing. Battery operation must quote cells, thermal management, charger power, replacement and depot fire arrangements. A complete comparison changes train mass and civil loads together with electrical cost.

### Control, safety and public information

The [equipment schedule](../../control-electronics/README.md) counts train protection channels, radios, car and door controllers, bogie brake controllers, service-power units, contact-shoe status, inverter controls, station dispatch, power-section gateways, grid protection and control-room equipment. Its **$102.536m** first-network and **$399.632m** citywide allowances are already inside the fourteen capital scopes; adding them again would double count. The train reserves 0.35 t and 6 kW for controls, with 299 kg and 3.68 kW currently scheduled. These are purchase and mounting allowances for the digital design.

Onboard protection grants traction only with a valid route, safe speed, contact and section status; loss of supply commands an independent stop. Door release depends on train identity, full stop, platform side and position. Wayside detection and interlocking protect occupied track; section isolation protects maintainers and evacuation. Control-room staff supervise service and incidents. The FUXA screen and historian can observe alarms and assets through the gateway; they do **not** issue movement authority or defeat onboard protection. Public displays receive an approved timetable, train-position and disruption feed with a safe fallback message. Software and schematic interface tests are development evidence; they do not establish a commissioned railway.

The systems integrator must deliver cable and connector schedules, isolated traction and control circuits, protection settings, section diagrams, event logs, software version records, access controls, fault response, recovery instructions and a trace between hazard, protective function, test and installed device. Independent braking, safe passenger egress, accessible boarding and fire protection remain fixed requirements in any cheaper option.

### Operating organisation and recurring cost

The operating company needs a staffed control room, station teams, train and electrical maintainers, civil inspection crews, cleaners, security, passenger assistance, stores and procurement, payroll and finance. The current annual operating figure combines **$2.60 per non-energy train-km**, **$1m per station-year**, grid energy at **$0.12/kWh**, and supply-specific upkeep. It is an allowance that includes operational work; it is not a payroll roster or an audited local wage bill. Staffing, shift premiums, training, spare parts, electricity tariffs and depot productivity should be priced as separate contract schedules before a fare or subsidy plan is adopted.

The published annual train-km assume every active train averages 38 km/h over 18 hours on every day. A detailed timetable should instead show peak and off-peak trips, dwell, turnbacks, empty movements, depot rotations, maintenance downtime and the six presently unassigned citywide sections. Passenger counts should come from demand and ticketing analysis, while the capacity table shows the offer that the train and interval could provide. The 30-year figure is a **present cost**, not forecast revenue, profit or loan repayment capacity.

## Iraqi factories and supply chain

Each alternative should buy repeatable assemblies through open drawings and inspectable specifications. The seven-corridor civil window needs a **minimum of five beam-casting yards and five erection fronts** at the modelled eight beams or lifts per workday per yard or front. The independent citywide civil window needs **at least nine of each**. Yard commissioning, curing space, shift patterns and street disruption need additional capacity or time; the present annual construction cash allocation has not separately priced that margin. These are production requirements within each alternative, not shared or already appointed factories.

| Work package | Intended Iraqi contribution | Procured or specialist input |
|---|---|---|
| Viaduct and foundations | Precast beams, piers, reinforcement cages, concrete, erection and repair | Bearings, stressing equipment and specialist testing where needed |
| Train cars | Carbody fabrication, doors and interiors, cable looms, final assembly and depot repair | Motors, converters, bearings and safety-critical controls initially |
| Stations | Structures, stairs, lifts installation, fit-out and passenger facilities | Certified equipment, fire and control components |
| Electrical railway | Cable routes, cabinets, installation, protection enclosures and routine maintenance | Contact equipment, switchgear and traction substations initially |
| Operations | Local staff, training, inspection, spares stores and renewal works | Initial specialist commissioning and training support |

The seven-corridor capital estimate includes **US$99.280m** for tooling, rescue and local-production setup; the independent citywide estimate includes **US$282.261m**. At the declared planning shares by contract scope, **US$12.599bn** of the citywide **US$25.848bn** non-contingency capital is addressable by Iraqi labour, materials, factories and engineering. This is a procurement target and contract-value opportunity, not an assertion that those orders have been placed or a deduction from the **US$31.018bn** total. The [scope-by-scope calculation](COST-AND-DELIVERY.md#local-production-and-design-rights) lets the city compare tender returns with the target.

The Iraqi public design custodian and participating manufacturers should receive the editable drawings, CAD, BOMs, control source, tooling files, inspection methods and revision history needed to **make, modify, repair and re-procure** the railway. The tender should require newly funded design work to be delivered under the applicable [OpenSourceRail licences](../../LICENSE.md) or separately assigned to the Iraqi public sponsor, and identify any supplier background rights, royalties and locked interfaces. Existing third-party map and component rights stay separately recorded. No hypothetical royalty saving is deducted from capital or operations; a bidder's priced alternative can expose that saving.

The industrial contract should link each physical assembly to an engineering drawing, part number, purchased material, approved supplier, manufacturing routing, inspection hold point, installed serial or batch number and maintainable asset record. ERP and purchasing handle quotations, purchase orders, stock, invoices, payroll, work orders and change control. CAD and structural analysis provide controlled design revisions; the digital twin connects those revisions to mass, electrical load, civil quantities and cost. None of these office systems may bypass railway protection controls. The local skills programme should cover casting and testing, carbody welding, harnessing, converter replacement, signalling installation, depot work and locally owned software maintenance.

| Production package | Factory or contractor deliverables | Handover into service |
|---|---|---|
| Representative six-car train | General arrangement, running gear and door interfaces, mass budget, power and cooling schematics, engineering and manufacturing bills of materials, assembly and inspection route | Serialised cars and bogies, software versions, spares, depot removal and rescue instructions |
| Repeatable viaduct span and support | Beam and bearing drawings, material and reinforcement schedules, lifting and temporary-work method, foundation family, inspection and transport records | As-built span and pier identifiers, tolerances, drainage and structural inspection plan |
| Station and electrical module | Platform and door datum, step-free circulation, signage, conductor and section diagrams, power cabinets, fire and isolation arrangements | Tested section and station identity, maintenance access, safe isolation and replacement process |

The city should procure designs and production rights with transparent make/buy schedules. A UK-supplied manufacturing line, tooling or specialist device can transfer process knowledge while Iraqi companies own and operate the yards, assembly plants and maintenance stores. The public sponsor should be able to buy replacements competitively from qualified suppliers using its retained drawings and data. A bidder claiming local content should state the Iraqi factory, material, labour, added value and work hours by assembly; a final imported box assembled locally should not be counted as full Iraqi manufacture.

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

Amanat Baghdad and the relevant Iraqi authorities would first settle the sponsoring and borrowing entity, procurement rights, land access, operating model, repayment source and government support. Civil, vehicle, power, signalling, station and depot contracts then use the same controlled railway design and bill of quantities. Iraqi public capital and Iraqi lenders can fund land, local production, buyer payments and the project reserve. UK export credit can support eligible UK-origin manufacturing equipment, specialist components, engineering, training and factory systems within separately priced export contracts.

### Proposed 20% UK equipment / 80% Iraqi production target

The 20/80 split below is an **industrial procurement scenario**, not today's measured content or a lending commitment. It is applied to **priced capital before the 20% project allowance**; the allowance has no assigned country of origin. UK-origin equipment and specialist export packages would be tendered as a proposed 20% share. Iraqi factories, contractors, engineering and assembly would be tendered for the remaining 80% of that priced portion. A true 80% Iraqi award needs matching specifications, domestic capability, accepted prices and quality control; the current model estimates only **$12.599bn**, or **48.7%** of the citywide priced portion, as presently addressable Iraqi contract value. Reaching the 80% target needs about **$8.079bn** of additional local scope, supply development or revised packaging.

| Funding and procurement scenario, US$ million | Seven corridors | Independent citywide |
|---|---:|---:|
| Priced capital before project allowance | 6,554.725 | 25,848.124 |
| Proposed UK-origin equipment and specialist contracts, 20% | 1,310.945 | 5,169.625 |
| Proposed Iraqi production and delivery, 80% | 5,243.780 | 20,678.499 |
| Project allowance, origin unassigned | 1,310.945 | 5,169.625 |
| **Installed capital** | **7,865.670** | **31,017.749** |

[UK Export Finance's Buyer Credit Facility](https://www.gov.uk/guidance/buyer-credit-facility) guarantees an acceptable bank's loan to an overseas buyer for an eligible export contract. Its published maximum is **85% of that contract**, with at least **15% paid directly by the buyer**; a UK exporter must carry on business in the UK, the export contract is at least **£5m**, and the repayment period is at least two years. [UKEF's foreign-content policy](https://www.gov.uk/government/publications/ukefs-approach-to-foreign-content/ukefs-approach-to-foreign-content) can allow up to 80% foreign content within an eligible supported contract with at least 20% UK content. That is a **contract-content rule**, not a promise to fund 80% of the Iraqi railway. [OECD local-cost rules](https://www.gov.uk/government/news/new-oecd-rules-on-support-for-local-costs) also restrict support for costs incurred in the buyer's country. The clean first financing case therefore places locally procured civil and factory contracts outside the UK export-credit contract unless UKEF confirms a specific eligible package.

If the entire proposed UK slice became an eligible Buyer Credit export contract and an acceptable bank lent at the published 85% ceiling, the **illustrative upper bound** would be as follows. It assumes no fees, premium, interest or exchange movement and does not treat a facility as approved or drawn.

| Illustrative Buyer Credit ceiling, US$ million | Seven corridors | Independent citywide |
|---|---:|---:|
| Proposed eligible UK export contract | 1,310.945 | 5,169.625 |
| Bank loan at 85% of that contract | 1,114.303 | 4,394.181 |
| Buyer cash on export contract, 15% | 196.642 | 775.444 |
| Iraqi production, project allowance and buyer cash needing other funding | 6,751.367 | 26,623.568 |

The seven-corridor illustrative loan is **14.17% of the installed railway cost**, not 85%; the independent citywide illustrative loan has the same proportion. The amount available may be much smaller. [UKEF's Iraq cover page](https://www.gov.uk/guidance/country-cover-policy-and-indicators) states medium/long-term cover is available for consideration and a **£1bn–£2bn market risk appetite**, subject to care on location; that is guidance rather than a project allocation. The citywide dollar illustration is much larger than this pound-denominated appetite; the exact comparison depends on exchange rates and existing exposures. A UK bank, UKEF, Iraqi sponsor and Iraqi lenders would need to agree tranche size, country capacity, security, repayment and draw schedule. [UKEF Direct Lending](https://www.gov.uk/guidance/direct-lending-scheme), ordinarily up to £200m per transaction, is a separate possible product and is **not** added to the Buyer Credit ceiling here.

### Funding each construction year

The annual capital draw above is a planning cash requirement, not a debt draw. At the same 20/80 sourcing target, **one sixth of each year's installed cash** is the proposed UK export package, **two thirds is Iraqi production** and **one sixth is the unassigned project allowance**. If the full UK package qualified at the 85% Buyer Credit ceiling, a bank could hypothetically provide **14.17% of each year's installed draw**, while the buyer and other lenders still provide **85.83%**, before financing charges. On the first network's $2.360bn peak annual draw, that illustrative bank share is about **$334m** and the remaining cash about **$2.025bn**. On citywide's $5.273bn peak draw, they are about **$747m** and **$4.526bn**. Actual export-credit payments follow equipment contracts and delivery milestones, so these annual proportions are a cash-planning sensitivity only.

Capital raising should proceed through a funded preparation phase; matched export, civil and rolling-stock tenders; bank and UKEF review of eligible contracts; Iraqi budget and lending approvals; and corridor-by-corridor financial close. The sponsor must also decide fare policy, public service payments, debt service, interest during construction, UKEF premium, foreign exchange and operating support. None is netted against the engineering capital estimate. Local public ownership of drawings and software lowers future dependency only when licences, tooling access and repair rights are written into the signed contracts.

## Delivery, governance and procurement sequence

The two alternatives have different scale and different funding decisions. For either one, the first contract package should produce a controlled corridor, station and utility register from the public maps; a service plan for every built section; the selected vehicle and power interfaces; and a bill of quantities that a factory and contractor can price. The city can then let repeatable civil, train, station, electrical and software packages against one configuration. Changes in train mass or power supply must flow to piers, energy, fleet, maintenance and annual cash before an option is compared.

| Period | Seven-corridor work | Independent citywide work |
|---|---|---|
| 2027–2028 | Sponsor and finance agreements, route and station definition, utility and land planning, first factory setup | Separate citywide corridor and service plan, station register, factory and grid strategy, finance tranches |
| 2028–2030 | Parallel precast, supports, stations, track, power and train production; minimum five casting and erection fronts in the civil window | Begin parallel corridors and factories; minimum nine casting and erection fronts for the 2028–2034 civil window |
| 2030–2031 | Integrate train, control and passenger information; inspect and open accepted corridors | Continue civil, station, train and electrical work and open completed connected sections |
| 2032–2035 | Operate, maintain and record the first alternative if selected | Complete citywide corridors, train delivery, integration and staged opening through 2035 |

Each corridor should have a contract schedule for land and utility access, materials, factory capacity, beam and station output, train delivery, power installation, installation inspection, software acceptance and cash draw. The sponsor must approve a safe opening plan for connected passenger service, including cross-city junctions and the unassigned citywide sections. The public PDF is a detailed planning and capital-raising proposal; the editable GIS, calculation input and controlled production drawings are the working records for tender development.

## Decision requested

Amanat Baghdad is asked to compare the two **independent** networks on coverage, capacity, installed and whole-life cost, local contract value and design rights. The citywide choice should safeguard through service to the airport, Sadr City and Jadriya and procure connected route, station, factory, power and finance packages. Tender returns should price local manufacturing, repair, training and transferable design deliverables against the same service specification.

**Basis of this proposal:** the published Iraqi route brief, open GIS place and population layers, the [Baghdad maps](maps/README.md), the [train](VEHICLE.md) and the [integrated cost schedule](COST-AND-DELIVERY.md). The maps and figures support a funding and procurement discussion. They do not claim surveyed alignments, supplier bids or operating approval.

## Sources and figure basis

The [Iraqi investment brief](https://investpromo.gov.iq/wp-content/uploads/2024/03/3.-RFI-English-%D9%86%D8%A8%D8%B0%D8%A9-%D8%B9%D9%86-%D9%85%D8%AA%D8%B1%D9%88-%D8%A8%D8%BA%D8%AF%D8%A7%D8%AF-E-20.2.2024.pdf) supplies the seven-line names, route-length controls and 64-station programme. OpenStreetMap, Natural Earth and Protomaps supply city context as recorded in the [map guide](maps/README.md). The separate citywide route input, the 280-station allowance and both networks' design, cost and annual cash figures come from [Baghdad system input](system.toml) and [calculated results](system-results.json), checked against the [cost schedule](COST-AND-DELIVERY.md). The [vehicle section](VEHICLE.md) and [control equipment schedule](../../control-electronics/README.md) define the installed planning interfaces. The sources are digital and public; no physical prototype, route survey, supplier quotation, signed loan or passenger-service certification is represented.

UKEF terms are from the [Buyer Credit Facility](https://www.gov.uk/guidance/buyer-credit-facility), [foreign-content policy](https://www.gov.uk/government/publications/ukefs-approach-to-foreign-content/ukefs-approach-to-foreign-content), [Iraq country-cover page](https://www.gov.uk/guidance/country-cover-policy-and-indicators), [OECD local-cost guidance](https://www.gov.uk/government/news/new-oecd-rules-on-support-for-local-costs) and [Direct Lending guidance](https://www.gov.uk/guidance/direct-lending-scheme), consulted 18 November 2026. The 20/80 industrial split and 85%-of-eligible-export calculation are explicitly labelled scenarios, and all source links remain active in the PDF.
