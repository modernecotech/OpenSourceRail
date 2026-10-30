# v0.6 station-powered freewheeling rail

OpenSourceRail aims for simple, affordable urban transport, repeated precast civil components and local manufacture and repair. Six lightweight comfort cars run on passive steel-wheel bogies and conventional rails. Station LIMs act on passive onboard aluminium secondaries; no onboard traction motor, traction battery or levitation magnet is fitted. Independent service power, braking and the existing station-led GoA4 architecture remain.

**Selected for reference engineering and prototype investigation. No physical, manufacturing or operating release.** The [selector](../../../engineering/development-baseline.toml) binds the same vehicle, body, support and propulsion identities through this packet, delivery records, Workbench and reader. [v0.5 maglev evidence](../../archives/v0.5-maglev/README.md) remains independently pinned.

| Item | Recalculated basis |
|---|---|
| Formation and comfort | Six 17 m cars; 104.5 m overall; 44 seats + two wheelchair places/car; zero planned standing |
| Running gear | 12 unpowered bogies, 24 axles, 48 wheels; independent friction/WSP/parking brake requirements |
| Body/platform | Retained lightweight aluminium/GFRP stock with revised bogie load paths; 1.0 m reference floor above rail |
| Accounted tare / normal load | 19.222 / 22.672 t/car at 75 kg/person |
| Located material / remaining reference accounts | 9.132 / 10.090 t/car |
| Complete installed mass, CG and inertia | Unknown; inherited service allocations may overlap new equipment and must be disaggregated |
| Service-only battery | 82.8 kWh, 1345 kg/car reference account; cooled installation and rail approval open |
| Service targets | 72 km/h, 0.4 m/s² acceleration, 0.6 m/s² braking, 35 s dwell, 120 s headway; 8,280 pphpd arithmetic |

## Reference journey and power

The 2 km, normal-load longitudinal requirement, including counted wheel/axle/disc rotational inertia, takes **147.362 s**, reaching 20 m/s and arriving at **16.559 m/s** before braking. Required peak launch force is **11.103 kN/car**, mechanical power **222.1 kW/car**. Actual available thrust, current, voltage and full motor efficiency remain unknown.

Full-train engagement requires **825.0 m** of shared launch/receiving winding; the library chooses **900 m**, **72 sections/direction** at 12.5 m and at least two independently controlled train branches. The **85.46 s** nominal berth interval is a necessary resource screen, not verified two-minute operation.

Reference profiles cover empty, 46-person and 160-person structural-control loads at 1.5 and 2 km, with grade/wind, charge and independent wet/downhill stopping bounds. A 0.05 adhesion hypothesis on a 2% downgrade gives approximately 700 m stopping from 20 m/s including one second response. Supplier brakes, WSP, uncertainties and actual routes must establish the protection envelope. Receiving motor recovery receives no safety credit.

The 82.8 kWh service reference uses 75 industrial Type3-20 modules plus explicit enclosure/cooling/conversion accounts. The 200 kW charging target passes a catalogue voltage/current necessary bound; available charge power versus SOC/temperature remains unknown. A 50°C environment exceeds the module ambient catalogue range. Normal 35 kW/car hotel duty balances in the prototype calculation; 50 kW/car adverse duty needs more charging. Solar yield is not guaranteed or credited to make the balance pass.

The actual GetDP conductive-slab benchmark converges against its exact imposed-field solution. It has no real primary winding, steel/end geometry, current-to-force map or finite-height return currents. Its conditional thrust is not available station thrust. Active-plate-only and all-aluminium heat-capacity bounds expose the dependence on thermal connection; actual temperatures remain unknown.

The [native physical follow-up](../v06-physical-closure/README.md) adds 18 current-excited LIM cases, 24 reduced Chrono brake runs and native body-interface/fit-up experiments. The tested full primary fails force and steel-field screens. Its raw field calculations remain conditional; the default geometry and acceptance holds are unchanged.

[Prototype/fault test plan](prototype-test-plan.json) · [Full evaluation](evaluation.json.gz) · [Motor method evidence](native-drive.tar.gz) · [Speed requirement](service-profile.svg) · [Equal-service comparison](comparison.json)

## Vehicle and civil design

New bogie hardpoints, deep side sills and retained roof longitudinal members replace the magnetic carrier arrangement. The isolated side sills fail their declared stiffness screen; ideal whole-body chord coupling is an upper stiffness bound, with shear transfer, openings and joints unqualified. Native CAD is counted material geometry, not a complete installed or collision-free certified vehicle. Split battery cassettes, brakes, suspension, couplers, frame joints and maintenance paths still need detailed installation.

The roof proposal uses HP60 core and a counted white finish; long-term loaded hot strength, durable reflectance and HVAC performance remain open. Unchanged door, glass, floor and seat stock retains its source ancestry; the revised vehicle receives a new identity. Plastic glazing remains an unqualified alternative.

Three conventional guideway families are compared across 15/20/25/30 m spans. The crowd-sized 20 m box reference counts **22.282 m³ concrete**, **2.408 t running rail**, **70 fastener sets** and **6.448 t total preliminary steel including rail, fasteners, reinforcement, tendons and anchorages. Its **62.15 t** span account still excludes complete bearings, piers, foundations, access/containment and station equipment.

New rails and fasteners are much lighter than the old magnetic interface stock, while concrete and remaining structural quantities have different boundaries. Lower installed cost is unproven. Each longitudinal section gets its own moving-load envelope; torsion, fatigue, unequal rail loads, prestress losses, erection and sites remain open. Twin and U sections retain their failures.

[Native vehicle material package](native-vehicle.tar.gz) · [Vehicle drawing](vehicle-overview.svg) · [Reference section](interface-section.svg) · [Civil alternatives](exports/civil.json) · [Partial native IFC](exports/selected-interface.ifc) · [IFC scope](exports/bim.json) · [BOM](exports/engineering-bom.json.gz) · [Processes](exports/manufacturing.json) · [Procurement](exports/procurement.json.gz) · [Assembly](exports/assembly.json) · [Controls](exports/controls.json)

## Sourcing and domestic cost coverage

The current sourcing seed contains **277 immutable records**: 55 sources, 16 product observations, 5 published price offers, 3 FX observations and 198 benchmarks. Iraqi source leads now include cement production, steel fabrication and rebar, GRP pipe and façade manufacturing, polymer/resin supply, and aluminium extrusion. Source leads are not quotations, qualified products or available capacity. See the [sourcing dossier](../sourcing/README.md) and [source-bound coverage index](../sourcing/validation.json).

The current selected physical candidate is `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`. The frame and federated sourcing runs instead use research candidates `1b3ae3f4de24f7302827e61047aa4ddb1f087c46ec84f47ec6bb2607b5a1e084` and `9c7d0942c9de6056e6afd051549273d0f34a72edf301fdd680ba37d12da7879f`. Their matching results, takeoff and cost screens do not transfer to the selected reference candidate.

| Research scope | Sourcing evidence | Cost disposition |
|---|---|---|
| Frame candidate `1b3ae3f4de24` | 3,183 groups; 0 compatible priced matches | Nine RFQ drafts remain unsent; complete installed cost unknown |
| Federated candidate `9c7d0942c9de` | 31,989 scopes in 7,042 sourcing groups; 137 evaluated, 6,905 pending | 0 compatible priced matches; all 137 evaluated purchase quantities unknown |
| Material takeoff `9c7d0942c9de` | 2,269 groups retain 27,216 located occurrences; 4,773 unlocated accounts stay separate | 4,780.58 t gross located stock and 1,804.81 m³ nominal concrete geometry are not installed mass or purchase quantities |
| Draft procurement-package BOM `9c7d0942c9de` | 27,216 located occurrences grouped into 191 hierarchy-based packages; 81 concrete spans carry 243 2025 local material/labour scenarios | 4,773 obligations remain separate; no supplier prices, order quantities or assembly completeness |
| Generic concrete fabrication screen | 3 material/labour recipes using September 2026 national materials and 2025 Baghdad wages; 2–8 skilled person-hours per nominal m³ | IQD 113,580–181,080/m³ with a 20% allowance; not a structural mix or guideway-beam price |

| 2026-price concrete takeoff estimate | 81 exact concrete manufacturing groups and 486 engineering occurrences, costed at 2/4/8 declared skilled h/m³ scenarios | IQD 205.0–326.8 million for gross modeled concrete volume; not a mix design, precast beam price or installed cost |
| 2025 Iraqi regional domestic-cost library | 102 material/labour scenarios across concrete, rebar, aluminium profiles and four Ur sheet forms; concrete recipe prices available in 12 of 15 listed governorates | Three governorates have missing concrete material prices; all scenario hours are assumptions and the 20% uplift is unallocated |
| 2025 Baghdad concrete takeoff estimate | 81 exact concrete manufacturing groups and 486 engineering occurrences, costed at 2/4/8 declared skilled h/m³ scenarios | IQD 207.0–328.9 million on the 2025 regional material rates; not a designed mix or installed span price |

| Unlocated obligation cross-references | 4,766/4,773 accounts linked by hierarchy to related car/bogie/span/bank scopes; 230 non-additive associations | No package mass, quantity or cost allocation; 7 network-level infrastructure obligations remain unlinked |
| 10 m² solid GFRP screen | IQD 1,229,647.35 known listed materials; 8/16/32 assumed skilled hours | IQD 1,565,576.82/1,655,576.82/1,835,576.82 partial materials + labour + 20%; unpriced inputs remain open |
| 10 m² sandwich GFRP screen | IQD 614,823.67 known listed materials; 8/16/32 assumed skilled hours | IQD 827,788.41/917,788.41/1,097,788.41 partial materials + labour + 20%; unpriced inputs remain open |
| 10 m² higher fibre sandwich GFRP screen | IQD 449,362.55 known listed materials; 8/16/32 assumed skilled hours | IQD 629,235.07/719,235.07/899,235.07 partial materials + labour + 20%; unpriced inputs remain open |

| 10 m² solid GFRP regional sensitivity | CSO skilled base wages in 15 listed governorates; hours are assumed, not measured | 8 h: IQD 1,535,576.82–1,566,077.22; 16 h: IQD 1,595,576.82–1,656,577.62; 32 h: IQD 1,715,576.82–1,837,578.42 after the 20% allowance; Kurdistan Region wage data are absent |
| 10 m² sandwich GFRP regional sensitivity | CSO skilled base wages in 15 listed governorates; hours are assumed, not measured | 8 h: IQD 797,788.41–828,288.81; 16 h: IQD 857,788.41–918,789.21; 32 h: IQD 977,788.41–1,099,790.01 after the 20% allowance; Kurdistan Region wage data are absent |
| 10 m² higher fibre sandwich GFRP regional sensitivity | CSO skilled base wages in 15 listed governorates; hours are assumed, not measured | 8 h: IQD 599,235.07–629,735.47; 16 h: IQD 659,235.07–720,235.87; 32 h: IQD 779,235.07–901,236.67 after the 20% allowance; Kurdistan Region wage data are absent |

The GFRP figures use listed Easy Composites UK material extensions converted at the 29 October 2026 CBI GBP/IQD reference and the 2025 CSO Baghdad or listed-governorate skilled-worker base-wage benchmarks. They are partial sensitivity screens: adhesives remain unresolved, sandwich-core prices are absent, and import, tooling, consumables, QA, fire/smoke, structural qualification and installation are excluded. The regional table covers only the 15 governorates in the CSO bulletin, excludes Kurdistan Region, and uses construction-worker wages as a proxy for composite-shop labour. They do not price a finished panel or transfer to the selected reference body.

The 2026-price estimate and the 2025 regional-price estimate are separately source-bound views of the same research-candidate concrete takeoff. Both preserve every original manufacturing-group and occurrence identity. Their material mix and labour hours remain assumptions, not measured process data; neither establishes a guideway beam, supplier match, complete installed mass or cost, or a cost for the selected reference candidate. The regional packet also includes rebar cut/bend and profile/sheet raw-stock processing sensitivities; the posted sheet rates do not establish structural grade or a completed manufacturing route.

The reference dossier's 900 m shared winding and the separate five-bank research layout (100 m active motor length) remain distinct propulsion configurations. Their force maps, electrical/thermal duties, plant quantities, procurement BOMs and installed costs are not shared.

## Automation, comparison and cities

Station-led GoA4, onboard ATP, OCC, TCMS, door control, interlocking and communications remain. New actual Rust wheel-interface fixtures check configuration/readiness and independent brake demands; existing ATP regressions remain software evidence. They use assumed readiness and have no physical brake plant or hardware outputs. Loss of propulsion leaves wheel support intact. Off-zone restart requires protected rescue/towing; mainline switches remain excluded, with depot exceptions only.

v0.6 is chosen for prototype investigation to remove the unproven levitation system and repeated magnetic-facing assemblies. It is heavier than the v0.5 accounted car and lighter than the optimistic stripped-v0.4 mass proxy. No same-service supplier-priced whole-life superiority is established. See the explicit comparison and open price coverage.

All **266 city geographies and maps are preserved**; **zero city performance packages are regenerated**. A metadata scan of 17,268 adjacent operating-stop gaps finds a longest retained gap of approximately 3 km in Faisalabad. Reference adverse cases test that distance; uphill unreachable cases and downhill speed-cap violations are retained. Historical city fleet, windings and finance figures are not v0.6 results.

[Geographic catalogue and holds](cities.json) · [Workbench](../../workbench/current/index.html) · [Native controls](native-controls.tar.gz)

## Iterative alternatives

The [failure-driven campaign](../v06-optimisation/README.md) generates body/motor/brake revisions, reruns native solvers, propagates the same mass into civil/service calculations and compiles matching research twins. The research winner is the next experiment; no qualified replacement is silently promoted. The comparison exposes normal/crowd deflection, additional mass and changed thrust requirements; conditional motor results remain outside their declared linear-steel domain. Participating-panel lateral displacement remains nonconverged under mesh refinement; its vertical values are diagnostic rather than validated full-body performance.

The [whole-railway architecture campaign](../v06-architecture/README.md) tests seven propulsion families, different speed/formation/powered-track arrangements and civil sections. It compares analytical demand and conditional quantities while keeping new equipment mass and actual motor capability unknown. Repaired finite-area joint/body and generic nonlinear magnetic method checks retain their independent numerical and engineering dispositions. No architecture is qualified, no city performance is regenerated and the selected v0.6 reference is preserved.

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
./osr legacy verify
```

[Source/payload receipt](manifest.json) · [README context](readme-coverage.md) · [Roadmap](../../ROADMAP.md) · [Project ethos](../../../README.md)

Selection id `8e5905bc7c81d6177bbaafde81ab3a5f8cc54947c4923eb4493949566ac85cdc`

Candidate id `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`

Body candidate id `9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117`

Support component id `3e9aef846e6ec55bac013512163394618b37cf8c74b1100d6f8e5450ae5479d7`

Propulsion component id `67e2bfc4ef429a6c49e6d07095bc298c4eb76b8386e4ee316c440ff128c30fa9`
