# v0.6 station-powered freewheeling rail

OpenSourceRail aims for simple, affordable urban transport, repeated precast civil components and local manufacture and repair. Six lightweight comfort cars run on passive steel-wheel bogies and conventional rails. Station LIMs act on passive onboard aluminium secondaries; no onboard traction motor, traction battery or levitation magnet is fitted. Independent service power, braking and the existing station-led GoA4 architecture remain.

**Selected for reference engineering and prototype investigation. No physical, manufacturing or operating release.** The [selector](../../../engineering/development-baseline.toml) binds the same vehicle, body, support and propulsion identities through this packet, delivery records, Workbench and reader.

| Item | Recalculated basis |
|---|---|
| Formation and comfort | Six 17 m cars; 104.5 m overall; 44 seats + two wheelchair places/car; zero planned standing |
| Running gear | 12 unpowered bogies, 24 axles, 48 wheels; independent friction/WSP/parking brake requirements |
| Body/platform | Retained lightweight aluminium/GFRP stock with revised bogie load paths; 1.0 m reference floor above rail |
| Accounted tare / normal load | 19.222 / 22.672 t/car at 75 kg/person |
| Located material / remaining reference accounts | 9.132 / 10.090 t/car |
| Complete installed mass, CG and inertia | Unknown; inherited service allocations may overlap new equipment and must be disaggregated |
| Mass reconciliation | [Occurrence-level ledger](../mass-reconciliation/current/README.md) and [closure worksheet](../mass-reconciliation/current/mass-closure-worksheet.json.gz) — 5,418 source, candidate-geometry and account-closure rows; 1,516 geometry parts retain exact source-geometry links (1,162.040 kg/car); 44 further parts (478.763 kg/car) match three declared source-component groups by exact aggregate mass; installed mass remains unknown |
| Service-only battery | 82.8 kWh, 1345 kg/car reference account; cooled installation and rail approval open |
| Service targets | 72 km/h, 0.4 m/s² acceleration, 0.6 m/s² braking, 35 s dwell, 120 s headway; 8,280 pphpd arithmetic |

## Reference journey and power

The 2 km, normal-load longitudinal requirement, including counted wheel/axle/disc rotational inertia, takes **147.362 s**, reaching 20 m/s and arriving at **16.559 m/s** before braking. Required peak launch force is **11.103 kN/car**, mechanical power **222.1 kW/car**. Actual available thrust, current, voltage and full motor efficiency remain unknown.

Full-train engagement requires **825.0 m** of shared launch/receiving winding; the library chooses **900 m**, **72 sections/direction** at 12.5 m and at least two independently controlled train branches. The **85.46 s** nominal berth interval is a necessary resource screen, not verified two-minute operation.

Reference profiles cover empty, normal-load and 160-person structural-control cases at 1.5 and 2 km, with grade/wind, charge and independent wet/downhill stopping bounds. A 0.05 adhesion hypothesis on a 2% downgrade gives approximately 700 m stopping from 20 m/s including one second response. Supplier brakes, WSP, uncertainties and actual routes must establish the protection envelope. Receiving motor recovery receives no safety credit.

The 82.8 kWh service reference uses 75 industrial Type3-20 modules plus explicit enclosure/cooling/conversion accounts. The 200 kW charging target passes a catalogue voltage/current necessary bound; available charge power versus SOC/temperature remains unknown. A 50°C environment exceeds the module ambient catalogue range. Normal 35 kW/car hotel duty balances in the prototype calculation; 50 kW/car adverse duty needs more charging. Solar yield is not guaranteed or credited to make the balance pass.

The actual GetDP conductive-slab benchmark converges against its exact imposed-field solution. It has no real primary winding, steel/end geometry, current-to-force map or finite-height return currents. Its conditional thrust is not available station thrust. Active-plate-only and all-aluminium heat-capacity bounds expose the dependence on thermal connection; actual temperatures remain unknown.

The [recorded native follow-up](../v06-physical-closure/README.md) contains 18 current-excited LIM cases, 24 reduced Chrono brake runs and body-interface/fit-up experiments under its original producer epoch. All seven original archives and 26 declared producer bindings are protected by a separate [source-epoch receipt](../retained-physical-followup-source-epoch/manifest.json); verify it with `python3 -m engineering.station_rail.closure_retention verify`. Current reference IDs match, but this byte/identity check performs no numerical re-execution, proves no physical equivalence and grants no current evaluator admission. The recorded full primary fails its declared force and steel-field screens; current physical acceptance remains open.

[Prototype/fault test plan](prototype-test-plan.json) · [Full evaluation](evaluation.json.gz) · [Motor method evidence](native-drive.tar.gz) · [Speed requirement](service-profile.svg) · [Equal-service comparison](comparison.json)

## Vehicle and civil design

The selected body uses bogie hardpoints, deep side sills and roof longitudinal members. The isolated side sills fail their declared stiffness screen; ideal whole-body chord coupling is an upper stiffness bound, with shear transfer, openings and joints unqualified. Native CAD is counted material geometry, not a complete installed or collision-free certified vehicle. Split battery cassettes, brakes, suspension, couplers, frame joints and maintenance paths still need detailed installation.

The roof proposal uses HP60 core and a counted white finish; long-term loaded hot strength, durable reflectance and HVAC performance remain open. Unchanged door, glass, floor and seat stock retains its source ancestry; the revised vehicle receives a new identity. Plastic glazing remains an unqualified alternative.

Three conventional guideway families are compared across 15/20/25/30 m spans. The crowd-sized 20 m box reference counts **22.282 m³ concrete**, **2.408 t running rail**, **70 fastener sets** and **6.448 t total preliminary steel including rail, fasteners, reinforcement, tendons and anchorages. Its **62.15 t** span account still excludes complete bearings, piers, foundations, access/containment and station equipment.

Rails, fasteners, concrete and the remaining structural quantities have separate accounting boundaries. Lower installed cost is unproven. Each longitudinal section gets its own moving-load envelope; torsion, fatigue, unequal rail loads, prestress losses, erection and sites remain open. Twin and U sections retain their failures.

[Native vehicle material package](native-vehicle.tar.gz) · [Vehicle drawing](vehicle-overview.svg) · [Reference section](interface-section.svg) · [Civil alternatives](exports/civil.json) · [Partial native IFC](exports/selected-interface.ifc) · [IFC scope](exports/bim.json) · [BOM](exports/engineering-bom.json.gz) · [Processes](exports/manufacturing.json) · [Procurement](exports/procurement.json.gz) · [Assembly](exports/assembly.json) · [Controls](exports/controls.json)

## Sourcing and domestic cost coverage

The current sourcing seed contains **533 immutable records**: 83 sources, 16 product observations, 5 published price offers, 3 FX observations and 426 benchmarks. Iraqi source leads now include the Ministry industrial directory, rebar and rolled steel profile suppliers, ordinary and sulphate-resistant cement producers, aggregate suppliers, EPS and polyurethane foam producers, aluminium ingot/alloy supply, metal fabrication, cable and busbar production, transformers, electrical enclosures and panels, precast concrete, GRP and façade manufacturing, polymer/resin supply, local composite-material distributors, and aluminium extrusion. Hadeed Iraq also provides a rebar marketplace/RFQ directory; displayed figures are indicative seller listings, not a binding Hadeed offer. Recent leads include [Diwan](https://www.diwan.com.iq/en/about) for Iraqi cables and transformers, [RS Al Najaf/IPDCO](https://ipdco.iq/najaf-factory/index.htm) for electrical cabinets and distribution equipment, and [Ibn Majid](https://www.ibnmajid.industry.gov.iq/uploaded_files/1730632596.pdf) for heavy steel/aluminium fabrication. The reviewed pages provide no candidate-matched prices or capacities; they are discovery leads, not quotations, qualified products or confirmed production availability. See the [sourcing dossier](../sourcing/README.md) and [current source-bound coverage index](../sourcing/validation-current.json).

The current selected physical candidate is `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`. The frame and federated sourcing runs instead use research candidates `1b3ae3f4de24f7302827e61047aa4ddb1f087c46ec84f47ec6bb2607b5a1e084` and `9c7d0942c9de6056e6afd051549273d0f34a72edf301fdd680ba37d12da7879f`. Their matching results, takeoff and cost screens do not transfer to the selected reference candidate.

The selected six-car vehicle now has its own source-bound Class C estimate for located geometry, named residual-account allowances, final assembly and a 50 km reference delivery. Its low/base/high account-cost and process-hour cases pair with the declared 0.8×/1.0×/1.2× residual-mass sensitivity; each case replaces the existing balance once, leaves the base tare unchanged, and does not claim installed mass. Candidate delivery exports also publish low/base/high process-hour work packages linked to cost lines and their source/occurrence identities; broad operation allocations remain open. The selected-candidate system estimate covers all 14 declared Class C cost scopes for a synthetic 6 km, three-station corridor. It evaluates 3 separate residual-mass cases against each of the low/base/high Class C cost cases. Each case replaces the residual accounts once, recalculates analytical journey demand, fleet basis, conditional energy, crowd-control beam quantities and minimum gravity footing-area screens under declared 300/200/100 kPa soil hypotheses. Footing-area costs remain separate fixed Class C proxies because route geotechnical design is unavailable. The base-mass case remains the published low/base/high estimate; all cases are assumptions, not a force-driven journey, site foundation design or physical acceptance. See the [selected vehicle cost record](exports/selected-vehicle-cost.json) and [selected system cost record](exports/selected-system-cost.json). Installed mass and possible account overlap remain unresolved; route-specific city costs, supplier quotes, physical journey performance and safety acceptance remain open.

| Research scope | Sourcing evidence | Cost disposition |
|---|---|---|
| Selected v0.6 vehicle `756a68870162` | Located geometry plus explicitly priced residual accounts; six cars; two 8 h production shifts; 50 km reference delivery | Candidate-bound Class C vehicle estimate; no route, civil or whole-life total |
| Selected-candidate synthetic system scenario `3c57229b4a4e` | 6 km periodic corridor; three stations; two service directions; 6 active + 2 reserve trainsets; all 14 scopes estimated; 3 residual-mass cases × 3 cost cases | Installed CAPEX IQD 58,240,649,181/282,459,494,179/1,706,670,107,280 low/base/high; whole-life NPV IQD 114,933,002,114/609,825,459,435/4,859,660,439,905; Class C only |
| Frame candidate `1b3ae3f4de24` | 3,183 groups; 0 compatible priced matches | Complete installed cost unknown |
| Federated candidate `9c7d0942c9de` | 31,989 physical scopes across 7,042 review requirements; 137 evaluated, 6,905 pending | 0 compatible priced matches; nine RFQ drafts remain unsent |
| Material takeoff `9c7d0942c9de` | 2,269 groups retain 27,216 located occurrences; 4,773 unlocated accounts stay separate | 4,780.58 t gross located stock and 1,804.81 m³ nominal concrete geometry are not installed mass or purchase quantities |
| Draft procurement-package BOM `9c7d0942c9de` | 27,216 located occurrences grouped into 191 draft packages and 8 purchasing/material lines; 52 domestic-source lead associations across seven families | 4,773 obligations remain separate; no supplier prices, commercial order quantities or complete assembly scope |
| Candidate sourcing sensitivity | 4 partial scenario spreads ranked; 4 material lines remain unranked. 1. civil/concrete/concrete-hypothesis: IQD 129.95m spread; 2. vehicle/body/aluminium_reference: IQD 23.67m spread; 3. wayside/primary/copper-conductor: IQD 2.53m spread; 4. vehicle/passive-secondary/6082-T6-proposed: IQD 2.23m spread | Scenario spread is not a probability range, cost bound or value-of-information estimate; gross stock masses are context only; no preferred-design change can be inferred |
| Generic concrete fabrication screen | 3 recipes using September 2026 Iraqi material and skilled-worker base-wage observations; 2/4/8 assumed person-hours per nominal m³ | IQD 113,580–181,080/m³ after materials + labour + 20%; not a designed mix or guideway-beam price |
| September 2026 concrete takeoff estimate | 81 exact concrete manufacturing groups and 486 engineering occurrences, with 2/4/8 assumed skilled h/m³ scenarios | Baghdad IQD 205.0–326.8m; Al-Muthanna IQD 196.9–294.3m, including 20%; ingredient screen, not a designed mix, precast beam price or installed cost |
| Candidate aluminium_reference raw-stock sensitivity | 21 distinct product-form/hour alternatives; mass and occurrence counts reconcile to the sealed takeoff | IQD 98.4–122.0m including direct material, assumed Baghdad base-wage labour and 20%; alloy/temper, product compatibility, purchase yield and process route remain unknown |
| Candidate 6082 T6 proposed raw-stock sensitivity | 21 distinct product-form/hour alternatives; mass and occurrence counts reconcile to the sealed takeoff | IQD 9.3–11.5m including direct material, assumed Baghdad base-wage labour and 20%; alloy/temper, product compatibility, purchase yield and process route remain unknown |
| 2025 Iraqi regional domestic-cost library | 102 dated material/labour scenarios across concrete, rebar, aluminium profiles and four Ur sheet forms; concrete recipe prices available in 12 of 15 listed governorates | Three governorates have missing concrete material prices; all scenario hours are assumptions and the 20% uplift is unallocated |
| 2025 Baghdad concrete takeoff estimate | 81 exact concrete manufacturing groups and 486 engineering occurrences, costed at 2/4/8 declared skilled h/m³ scenarios | IQD 207.0–328.9 million on the 2025 regional material rates; not a designed mix or installed span price |
| Unlocated obligation cross-references | 4,766/4,773 accounts linked by hierarchy to related car/bogie/span/bank scopes; 230 non-additive associations | No package mass, quantity or cost allocation; 7 network-level infrastructure obligations remain unlinked |

| GFRP study | Labour basis | Partial cost |
|---|---|---|
| 10 m² solid GFRP screen | IQD 1,229,647.35 known listed materials; 8/16/32 assumed skilled hours | IQD 1,565,576.82/1,655,576.82/1,835,576.82 partial materials + labour + 20%; unpriced inputs remain open |
| 10 m² sandwich GFRP screen | IQD 614,823.67 known listed materials; 8/16/32 assumed skilled hours | IQD 827,788.41/917,788.41/1,097,788.41 partial materials + labour + 20%; unpriced inputs remain open |
| 10 m² higher fibre sandwich GFRP screen | IQD 449,362.55 known listed materials; 8/16/32 assumed skilled hours | IQD 629,235.07/719,235.07/899,235.07 partial materials + labour + 20%; unpriced inputs remain open |

| Regional GFRP scenario | Wage basis | Partial cost sensitivity |
|---|---|---|
| 10 m² solid GFRP regional sensitivity | CSO skilled base wages in 15 listed governorates; hours are assumed, not measured | 8 h: IQD 1,523,576.82–1,565,576.82; 16 h: IQD 1,571,576.82–1,655,576.82; 32 h: IQD 1,667,576.82–1,835,576.82 after the 20% allowance; Kurdistan Region wage data are absent |
| 10 m² sandwich GFRP regional sensitivity | CSO skilled base wages in 15 listed governorates; hours are assumed, not measured | 8 h: IQD 785,788.41–827,788.41; 16 h: IQD 833,788.41–917,788.41; 32 h: IQD 929,788.41–1,097,788.41 after the 20% allowance; Kurdistan Region wage data are absent |
| 10 m² higher fibre sandwich GFRP regional sensitivity | CSO skilled base wages in 15 listed governorates; hours are assumed, not measured | 8 h: IQD 587,235.07–629,235.07; 16 h: IQD 635,235.07–719,235.07; 32 h: IQD 731,235.07–899,235.07 after the 20% allowance; Kurdistan Region wage data are absent |

The GFRP figures use listed Easy Composites UK material extensions converted at the 29 October 2026 CBI GBP/IQD reference and September 2026 CSO Baghdad or listed-governorate skilled-worker base-wage benchmarks. They are partial sensitivity screens: adhesives remain unresolved, sandwich-core prices are absent, and import, tooling, consumables, QA, fire/smoke, structural qualification and installation are excluded. The regional table covers only the 15 governorates in the CSO bulletin, excludes Kurdistan Region, and uses construction-worker wages as a proxy for composite-shop labour. They do not price a finished panel or transfer to the selected reference body.

The selected-candidate 6 km system estimate now includes a 36-case service-energy sensitivity across the 50/75-module battery alternatives, 50/75/100% catalogue-current acceptance hypotheses, low/base/high 150/200/250 kW-per-car charging cases, and 35/50 kW-per-car hotel loads. The selected 75-module pack's base 200 kW, 35-second-stop case has calculated margins of 0.074 kWh/car reference and -0.686 kWh/car adverse; the adverse deficit is 0.686 kWh/cycle, or about 60.9 idealized cycles across the declared hot end-of-life SOC window. This linear reserve screen is not repeated-duty qualification or a supplier charge map. A theoretical full-roof PV case at 4 equivalent peak-sun-hours/day yields 30.3 kWh/car-day, at most 4.8% of the base 35 kW, 18-hour hotel-load energy; PV area/layout, output timing, mass and capital cost remain unverified, and no solar energy is credited to the per-cycle balance. A separate 50 kW/car station-fed hotel branch would supply 0.486 kWh during the stop but leaves the adverse cycle short by 0.199 kWh. Its 1.8 MW six-platform Class C power-package/installation screen is IQD 0.945/3.780/15.120 billion, excluding grid upgrades, connectors and protection; it requires a new system candidate and is not added to selected-system costs. An independent continuous service source would need 35/50 kW per car and 560/630/1,200 kWh per car-day under the low/base/high shift cases, but no source technology, mass or cost is selected. All sensitivities are research estimates; none changes the selected hardware or establishes service qualification, physical feasibility, supplier pricing or release.

The September 2026, July 2026 and 2025 price views remain separately dated source-bound estimates. The September concrete takeoff preserves all 81 manufacturing groups and 486 occurrences across Baghdad and Al-Muthanna scenarios. The aluminium alternatives apply exact aggregate takeoff masses while retaining their group and occurrence identities through the takeoff ID; they do not assign a form or supplier SKU to individual occurrences. Material mix and labour hours remain assumptions, not measured process data; these scenarios do not establish a guideway beam, supplier match, complete installed mass or cost. The selected reference has separate vehicle and synthetic-corridor Class C estimates; city-specific civil and whole-life costs remain open. The regional library also includes rebar cut/bend and profile/sheet raw-stock processing sensitivities; posted sheet rates do not establish structural grade or a completed manufacturing route.

The separate five-bank, 100 m active-length research configuration now has a copper raw-stock sensitivity in the [candidate-bound procurement packet](../sourcing/procurement-bom/federated-v06-research-packages-v24.json.gz): 9.354 t across five bank groups and ten retained occurrences, using a 2025 Iraqi CIF copper-wire unit-value benchmark, September 2026 Baghdad base wage, 8/16/32 assumed labour hours per tonne and a 20% uplift. The partial totals are IQD 90.19/91.03/92.72 million. They do not establish winding-conductor compatibility, a measured winding route, complete station-drive cost or the selected reference's approximately 900 m winding allocation. Supplier, force, current, heat-rejection and repeated-duty evidence remain open. Five source-bound unsent bank scopes and their comparable duty/evidence request are in the [station-drive RFQ draft](../sourcing/rfq-drafts/station-drive-banks-2026-10/README.md); the [current sourcing validation index](../sourcing/validation-current.json) records its candidate, quantities and open evidence gates.

The [CSO 2024 construction-wage archive](../../../engineering/sourcing/data/iraq-construction-wages-2024.json) preserves Table 7 daily wage observations for 15 governorates and six categories, normalized here by an explicit 8-hour workday. Baghdad skilled labour is IQD 75,000/day or IQD 9,375/hour. This is historical base-wage context, excludes employer burden and Kurdistan Region, and is not used in current 2025/2026 estimates; the current fabrication screens use dated material and wage rates, assumed hours, then a 20% uplift.

The reference dossier's 900 m shared winding and the separate five-bank research layout (100 m active motor length) remain distinct propulsion configurations. Their force maps, electrical/thermal duties, plant quantities, procurement BOMs and installed costs are not shared.

## Automation, comparison and cities

Station-led GoA4, onboard ATP, OCC, TCMS, door control, interlocking and communications remain. New actual Rust wheel-interface fixtures check configuration/readiness and independent brake demands; existing ATP regressions remain software evidence. They use assumed readiness and have no physical brake plant or hardware outputs. Loss of propulsion leaves wheel support intact. Off-zone restart requires protected rescue/towing; mainline switches remain excluded, with depot exceptions only.

The selected wheel-supported reference uses station propulsion with passive onboard reaction elements. No same-service supplier-priced whole-life superiority is established; candidate comparisons and open price coverage remain in this dossier.

All **266 city route geographies and stop locations are available as planning inputs**; **zero v0.6 city performance packages are published**. Current city stop geography identifies a 7.000 km adjacent-stop gap in Dar Es Salaam; it supplies a bounded adverse-distance scenario only. No city journey or operating result is inferred from the scan.

[Geographic catalogue and holds](cities.json) · [Workbench](../../workbench/current/index.html) · [Candidate delivery exports](exports/manifest.json) · [Native controls](native-controls.tar.gz)

## Iterative alternatives

The [failure-driven campaign](../v06-optimisation/README.md) generates body/motor/brake revisions, reruns native solvers, propagates the same mass into civil/service calculations and compiles matching research twins. The research winner is the next experiment; no qualified replacement is silently promoted. The comparison exposes normal/crowd deflection, additional mass and changed thrust requirements; conditional motor results remain outside their declared linear-steel domain. Participating-panel lateral displacement remains nonconverged under mesh refinement; its vertical values are diagnostic rather than validated full-body performance.

The [whole-railway architecture campaign](../v06-architecture/README.md) tests seven propulsion families, different speed/formation/powered-track arrangements and civil sections. It compares analytical demand and conditional quantities while keeping new equipment mass and actual motor capability unknown. Repaired finite-area joint/body and generic nonlinear magnetic method checks retain their independent numerical and engineering dispositions. No architecture is qualified, no city performance is regenerated and the selected v0.6 reference is preserved.

The [interrupted-case reachability supplement](../architecture-reach-closure/README.md) applies a conservative off-power stopping bound to three 600-second interrupted P3 scenarios. Conditional on their recorded states and unchanged command windows, each stops more than 445 m short of its next target. The original interrupted traces remain unchanged; this is an analytical infeasibility result rather than demonstrated train stopping or a completed journey.

The [20 m civil shape portfolio](../civil-shape-portfolio/README.md) generates 18 explicit box, ribbed, varying-depth, folded and hybrid geometries. Calculated stock and surface quantities feed two-shift manufacturing, delivery, scoped installed and lifecycle cost scenarios. Its [gross-elastic mechanics follow-up](../civil-shape-mechanics/README.md) adds 189 same-train load/mass/hypothesis calculations, model-only moving-load deflection bounds and lifting-related cost revisions. These preserve stiffness/cost alternatives without validating cracking, resistance, composite action, lifting or a civil replacement.

The separate [flanged-girder study](../flanged-span-study/README.md) calculates three 20 m steel-girder and concrete-deck configurations against the same selected vehicle and mass scenarios. Its steel-only beam model, full-moment splice assumption and scoped per-span costs remain unqualified; it does not select a railway or establish whole-system economics.

Its [same-service cost scenarios](../flanged-system-cost-study/README.md) propagate the three configurations through fourteen provisional cost scopes with common rates and two-shift delivery assumptions. The [reference geometry changes by mass case](../flanged-system-cost-context.md). Whole-life differences against the canonical reference remain held until coating and bearing renewal scopes match; foundation prices and site capacity remain unresolved.

The separate [matched-renewal research](../matched-renewal-research/README.md) introduces explicit hypothetical reference bearings, concrete-treatment alternatives and maintenance-overlap sensitivities. It compares fifty-four conditional cases with each reference beam identity preserved; it neither changes the selected reference nor qualifies or ranks a railway.

The [conditional mass and support sensitivity](../installed-mass-support/README.md) replaces named residual accounts once and varies their assumed longitudinal positions across the car. It computes correlated two-bogie reactions, not axle loads or verified installed mass; component positions and potential account overlap remain open.

The [conditional repeated-duty thermal study](../periodic-thermal-research/README.md) reconstructs the selected P1 synthetic 500 m command-window loss trace and compares two 120-second cooling assumptions. The high case remains held after a controller limit; no fixed-bank cooling, actual motor performance or 900 m winding is qualified.

The [implicit-geometry experiment](../implicit-geometry-study/README.md) preserves a three-dimensional sampled gyroid volume and VTK bytes with separate physical and evaluation identities. Its sampled material mass excludes installation; its continuous surface, manufacture and structural behavior are unqualified.

The completed [bounded wheel campaign](../v06-optimisation/README.md) has its top-level campaign producer bindings pinned in a separate [source-epoch receipt](../retained-wheel-source-epoch/manifest.json). Verify that archive with `python3 -m engineering.design_search.retained_publication verify`. Nested attempt archives remain byte-for-byte preserved; additional per-attempt source coverage and numerical re-execution are not claimed. This check grants no admission under current evaluators or current design selection. Continuing architecture and adaptive studies use their current source contracts.

The [function-first adaptive generator](../v06-adaptive-design/README.md) separates mandatory obligations, advisory targets, revisable hypotheses and numerical model domains. Its extensible material/structure/joining/equipment/system variables drive coupled revision tasks. New thinner/deeper sill experiments redistribute counted material, with native normal/fine/crowd cases and matched mass, axle, demand and civil calculations. Provisional deflection alone neither rejects nor accepts a car; local stability, strength, joints, clearances and correlation remain open.

The [generative structural campaign](../generative-structure/README.md) composes different physical body arrangements, generates actual stock and interface graphs, diagnoses mechanisms and executes topology, layout and function-integration rewrites. Gross structure stock is not equipped vehicle tare. Native axial underfloor checks and CAD exports do not validate complete shell, laminate, joint or vehicle response; no integrated design is selected.

The [coordinated railway experiment](../coupled-railway/README.md) connects architecture, adaptive proposals, generated bodies, inventory, motor requirements, independent braking, civil loads, manufacturing and economic coverage through one versioned bundle and dependency graph. Changed body stock automatically triggers downstream evaluation. New three-dimensional metal-body research and conditional operating requirements retain their exact models and missing evidence; complete installed mass, available nonlinear LIM capability and a qualified journey remain open.

The [candidate-to-journey closure matrix](../railway-closure/README.md) propagates three distinct bodies through separate 1.5 km and 2 km station-only/recovery-research bundles, empty/normal/crowd/adverse demand, independent brake hypotheses, civil and cost quantities. Its fault journeys remain not-run. The [moving-conductor LIM experiment](../moving-lim-method/README.md) translates the actual secondary through a voltage-coupled field model; unresolved refinement and high-speed domain limits prevent force-map admission. Neither experiment supplies a complete equipped vehicle or physical journey.

## Readiness and reproduction

| Gate | State | Evidence still needed |
|---|---|---|
| installed-vehicle | **unknown** | Locate and weigh all residual stock, joinery, bogie and service assemblies; obtain complete CG and inertia. |
| isolated-underframe-stiffness | **fail** | The isolated hollow side-sill fixtures exceed the declared deflection limit. Whole-body load sharing through retained longitudinal members, posts and joints must be demonstrated or redesigned. |
| body-and-bogie-structure | **unknown** | Concentrated bogie support changes the body load path. Local/frame fixtures do not establish joined-body stress, buckling, fatigue, crash, modes or bogie qualification. |
| wheel-rail-dynamics | **unknown** | Qualify wheel profiles, hunting, curves, suspension, ride, flange forces and derailment containment. |
| station-LIM-force-map | **unknown** | No accepted thrust/current/frequency/gap/temperature map for the complete station drive and moving secondary; targets are required forces. |
| station-electrical-thermal | **unknown** | Qualify inverters, section handoff, supply, slip/secondary heat, unwanted normal forces and 120-second repeated duty. |
| independent-braking | **unknown** | Validate supplier brake/WSP/adhesion/thermal curves, channel failures, parking, receiving-power loss and degraded gradients. |
| hot-weather-services | **unknown** | HVAC delivered capacity and COP at 50 C, roof long-term structural temperature and actively cooled service pack remain unqualified. |
| coupled-journey | **unknown** | Reference motion is analytical. Required physical drive/brake maps, wheel dynamics and flexible-body model are not available for a qualified six-car trip. |
| GoA4-protection | **unknown** | Existing Rust ATP/interlocking and new wheel interface predicates require candidate-correlated braking, sensing, timing, communications and fault evidence. |
| civil-and-site | **unknown** | Alternative sections are necessary screens. Prestress, fatigue, torsion, lateral/derailment loads, foundations, survey, erection and independent review remain open. |
| rescue-and-evacuation | **unknown** | Motorless off-zone restart needs a protected rescue/tow system, emergency access and an acceptable high-viaduct evacuation plan. |
| whole-system-economics | **unknown** | No same-service supplier quotes or complete CAPEX/OPEX/renewal comparison; lower installed cost has not been established. |
| city-regeneration | **hold** | Preserve 266 geographic inputs. Numerical city publication is held pending reference propulsion, braking, route and economic evidence. |

```bash
./osr status
./osr build
./osr verify
./osr test
./osr book --check
./osr sim baghdad  # explicit city evaluation hold
./osr twin export
```

[Source/payload receipt](manifest.json) · [README context](readme-coverage.md) · [Roadmap](../../ROADMAP.md) · [Project ethos](../../../README.md)

Selection id `8e5905bc7c81d6177bbaafde81ab3a5f8cc54947c4923eb4493949566ac85cdc`

Candidate id `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`

Body candidate id `9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117`

Support component id `3e9aef846e6ec55bac013512163394618b37cf8c74b1100d6f8e5450ae5479d7`

Propulsion component id `67e2bfc4ef429a6c49e6d07095bc298c4eb76b8386e4ee316c440ff128c30fa9`
