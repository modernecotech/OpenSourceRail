# OpenSourceRail delivery roadmap

The [Baghdad Airport audit](../cities/Baghdad/engineering/simulation/AUDIT-RESULTS.md) links the revised route, service and budgetary enquiry. The [prototype review](../cities/Baghdad/engineering/prototype/README.md) retains the earlier first-article drawings and records the outstanding physical decisions.

OpenSourceRail connects three products: city planning and service, railway engineering and manufacturing, and controls and maintenance. Local design, fabrication, repair and open knowledge are the governing economic aims. The [project introduction](../README.md) explains the full platform; the [architecture](ARCHITECTURE.md), [engineering status](ENGINEERING-STATUS.md), [cost baseline](COST-BASELINE.md) and [v0.7 release record](RELEASE-v0.7.md) are the current decision documents.

Start with the [stakeholder partnership plan](operator-review/PARTNERSHIP-PLAN.md) to recruit a host, test one workflow with local evidence and decide whether to fund a bounded study. It proposes owners, an engagement budget and a decision at week twelve.

The [railway delivery workplan](operator-review/WORKPLAN.md) assigns the first twelve weeks of core and Baghdad work to operators, engineers, local manufacturers and sponsors. Use the [operator briefing and design twins](operator-review/README.md) to review the proposals with them.

The Baghdad metropolitan network joins the Airport and three named suburbs through shared interchanges, three rings and four cross-Tigris trunks. Its planning prices, shift schedules and curved-beam takeoffs use the same mapped network. Detailed service, site and construction checks remain open. [Network](../cities/Baghdad/METROPOLITAN-NETWORK.md) · [Current quantities and delivery](../cities/Baghdad/METROPOLITAN-DELIVERY.md)

The [Airport GIS simulation](../cities/Baghdad/engineering/simulation/GIS-SIMULATION.md) shows how public terrain, soil and water layers can replace uniform desktop inputs and drive simulated construction quantities, operating cases and whole-life costs.

## Published digital releases

| Release | Result | Scope |
|---|---|---|
| [v0.6.1](https://github.com/modernecotech/OpenSourceRail/releases/tag/v0.6.1) | Published open engineering platform | Passive wheel development reference, software and research tools; [installation record](releases/v0.6.1/installation-verification.md) |
| [v0.7.0](https://github.com/modernecotech/OpenSourceRail/releases/tag/v0.7.0) | Published digital engineering package | Selected powered-wheel 30 km reference, cost, delivery, CAD/FEM evidence, production handoff and Workbench journey |
| [v0.7.1](https://github.com/modernecotech/OpenSourceRail/releases/tag/v0.7.1) | Baghdad and control update | Independent Baghdad networks, city maps, elevated railway costing and control electronics quantities |
| [v0.7.2](https://github.com/modernecotech/OpenSourceRail/releases/tag/v0.7.2) | Baghdad Airport integration | Connected workings, feeder outage checks, preliminary quantities, supplier dossier and phased investment |

The v0.6 passive vehicle, the v0.7 synthetic 30 km railway, the Samawah case and the Baghdad protected-conductor network have separate candidate identities and cost assumptions. A change in one does not revise the others. The [v0.6 engineering findings](design-engine/v06-design-closure/README.md) and [maglev archive](archives/v0.5-maglev/manifest.json) remain historical research, outside current release checks.

## Status against project goals

The current Airport comparison uses a 17.46 km horizontal study. The 30-minute paired-supply trial completes 72 booked trips. Stations and levels need survey, and priced lots and physical acceptance remain open. The [published v0.7.2 opening](../cities/Baghdad/airport-integration.html) retains the earlier 12 km, 15-minute case. [Current audit and enquiry](../cities/Baghdad/engineering/simulation/AUDIT-RESULTS.md)

| Project goal | Where we stand | Change needed |
|---|---|---|
| Affordable, frequent urban transport | The 30 km digital railway reconciles fourteen capital scopes at $34.17m per route-km. Baghdad prices two independent elevated networks and models an hourly service offer. The citywide budget includes 50.099 km of reserved guideway. | Use the published reserve cost when deciding which sections to open. Use the connected train diagrams to resolve peak block occupancy, terminal platform access and the five deferred access sections in the 14-group mainline option before selecting an opening service. |
| Simple trains and standard civil works | The passive-wheel development reference retains its aluminium secondary interface. The tested station-only launch cases stalled in the published uphill screens. The powered synthetic reference and Baghdad's trackside supply add equipment. Baghdad's protected conductor has a small estimated cost lead over overhead, sensitive to assumed prices. | Compare station launch, launch with bounded assist and powered wheels on the same duty. Develop lighter and simpler hardware where the reductions persist through civil work, grid demand, maintenance and renewal. |
| Local manufacture, repair and open design knowledge | The reference has a car and span model, a 52-row BOM and a 23-step production plan. Baghdad and the synthetic estimate use assumed local work rates. | Make the local scope visible when an estimate changes. Use the [Airport factory schedule](../cities/Baghdad/engineering/prototype/FACTORY-SPECIFICATION.md) to obtain matched equipment, hire and service offers. Confirm material origin, shop hours and replaceable assemblies through a first-article and repeat run. |
| Safe and accessible travel | The repository has controls simulations, independent braking requests, platform interfaces and equipment schedules. | Carry the same loading, station and power assumptions through degraded braking, door release, clearance, recovery and electrical protection. Record separate evidence for CAD/FEM and later physical qualification. |
| Connected open delivery tools | Workbench recalculates selected quantities and costs. ERPNext/Frappe HR has draft workflows, and FUXA and the gateway support supervision. Historical checks now have narrower triggers. | Show when a Workbench result changes the scope of a baseline handoff. Exercise estimate, purchase, production, QA and maintenance against the same assembly while keeping the supervision and train authority interfaces distinct. |

## Delivery sequence

### v0.8 Airport integration work

Use the [Baghdad Airport digital project reference](../cities/Baghdad/engineering/simulation/PROJECT-REFERENCE.md) for the next joined engineering run. It fixes the provisional GIS-profiled route, 30-minute service, six-car powered-wheel train and paired six-site supply for that run. A passing booked-day simulation leaves the failed and open functional checks in force. Record a new physical candidate when an interface or installation changes.

| Phase | Lead and next work | Evidence needed to close the phase |
|---|---|---|
| 1. System definition | Systems and operations verify the centreline, stops, demand, turnbacks and depot access. Allocate each load, clearance, protection and service requirement to an interface owner. | One requirements and hazard register, with the route, train, civil, power and price identities reconciled. Check clean installation and source-bound outputs. |
| 2. Operating model and controls | Controls, rolling stock and electrical run the candidate-specific authority and braking sensitivities. Add actual proposed protection boundaries and measured actuator response when available. Size the auxiliary duty and protection equipment with the same load and recovery scenarios. | Working-day and degradation records plus an independently checked stopping and isolation envelope. Record unresolved adequacy, localisation, network timing, hardware independence and bench evidence by owner. |
| 3. Representative assemblies | Rolling stock and civil close one car, one bogie, one station and the 20 m repeat bay. Compare the operating loads with prestress release, handling, road lifts and loaded flatbed and gantry stages. | Common interface datums, installed weight and axle reactions, platform sweep, structural checks, the foundation basis and a temporary works design. Use the assembly register to request scope-matched returns. |
| 4. Production and economics | Production, procurement and the operator reconcile EBOM, shop routing, site work and renewals on the confirmed assembly. Use the existing Rust workplan, delivery schedule and 30-year ledger. | Traceability from quantities to supplier rows and roles, checked for duplicated work and missing cost scope. Record inspection, repair and replacement methods and the basis for Iraqi content. |
| 5. Digital review and first articles | The integrator and an independent reviewer rerun the same project input and challenge a changed vehicle mass, a stale authority and a changed civil quantity. Publish the engineering, procurement and operations evidence in one reader. | Current sources, reproducible outputs and review records. Issue fabrication and operating approvals only through their respective evidence and decision processes. |

Begin with the [requirements and standards crosswalk](certification/compliance-matrix.md), the [Airport ATP replay](../cities/Baghdad/engineering/controls/AIRPORT-ATP.md) and the [assembly cost and workplan](assets/assembly-animations/GUIDE.md#parts-cost-and-shifts).

| Priority | Work | Completion check |
|---|---|---|
| 1. Make the price reviewable | Show buyers which costs serve scheduled trains, which cover reserved sections and which packages local suppliers can deliver. Make these quantities visible when a station or route changes. | Capital reconciles to the selected totals. A station edit recalculates local work. Candidate identities and existing service and prices are preserved. |
| 2. Establish the service envelope | Build a connected schematic service graph from named sections and explicit junctions. Screen stop locations against GIS and derive dwell, turnback and peak fleet. Model one construction opening using station, utility, train and power readiness alongside beam output. | Every costed section has a purpose. Every offered passenger journey has an explicit path, cycle and station screen. Opening dates follow dependencies and identified resource costs. |
| 3. Compare simple architectures and structures | Extend the [existing equal-service motion comparison](design-engine/v07-architecture-decision/README.md) through the [coupled railway campaign](../campaigns/coupled-railway-design.toml) and [architecture search](../campaigns/whole-railway-architecture-search.toml). Screen route, acceleration, energy and braking limits before pricing viable alternatives. Evaluate shared piers and longer spans against the same train loads and erection limits. | Each alternative has its own mass, interfaces, stopping and recovery envelope, civil quantities and cost. Rank only cases with comparable service and priced scope. |
| 4. Tie design to production and upkeep | Take one car assembly, span and station equipment package from interface drawing through quoted BOM, shop route, inspection and replacement. Exercise ERPNext/Frappe HR handoff and FUXA observation with the same equipment records. | Workbench, CAD/BIM, BOM, tooling, QA, repair and the cost estimate identify the same design revision. A changed design identifies which handoff must be refreshed. |
| 5. Issue a coordinated design revision | Issue the revised route map, estimate, drawings, operating assumptions and revision notes together so planners, suppliers and operators can use the same edition. | Generated results reconcile, affected checks pass and the release states the maturity of each deliverable. |

GIS, CAD, FEM and simulation support the digital work above. Supplier quotes, site investigations, authenticated physical measurements and independent approval remain project inputs for procurement, fabrication and operation. The [release record](RELEASE-v0.7.md) describes the published digital scope.

## Workshop and station trials

- **Bogie and body fit.** On the passive reference car, rotate the bogie under the sill and measure the gap to the wheel hub. On the powered reference train, test the brake mounting and rail fastening under the load of a delayed downhill stop. [Reference test assemblies](../engineering/interface_studies/REFERENCE-RIGS.md)
- **Local manufacture.** Quote the Baghdad carbody and bogie-frame stock by part. Check the door openings and suspension seats on the first welded assembly. At a typical station, trial the deck panels, beam bearings, drainage and replacement access. [Frame stock and drawing](../cities/Baghdad/engineering/mechanical/vehicle/README.md) · [Station and viaduct sections](../cities/Baghdad/engineering/mechanical/civil/README.md)
- **Boarding and dispatch.** Demonstrate the parking hold throughout boarding and the transfer to traction after every door locks. The secured-berth replay now permits normal door opening. Instrument a loaded brake and traction rig to measure the handover on a gradient. [Station controls and wiring](../cities/Baghdad/engineering/controls/README.md)

## Baghdad work following the corridor review

Prepare the open proposal for an anticipated late-2026 to early-2027 invitation for new ideas. Confirm the timetable and updated scope with the authority when it issues the opportunity. The [proposal](../cities/Baghdad/PROPOSAL.md) records the October Arabic-language interviews on the earlier unsuccessful offers and the new study.

| Decision | Evidence in hand | Work needed for the decision |
|---|---|---|
| Where to protect land | The [place-name review](../cities/Baghdad/maps/README.md#locating-the-names-in-the-brief) records 39 located occurrences and 13 gaps. | Prioritise shared unresolved names, verify the Adhamiya and airport access points with local owners, obtain referenced alignments and walk the proposed interchanges. Reconcile revised chainage to each line allowance before repricing. |
| How to buy and fund a line | The [proposal](../cities/Baghdad/PROPOSAL.md) compares annual buyer cash for four capital structures. The [bid return schedule](../cities/Baghdad/BUYER-COMPARISON.md) records item prices, rights and Iraqi value added. | Reprice the [revised Airport route](../cities/Baghdad/engineering/simulation/AUDIT-RESULTS.md) with survey quantities, power capacity and quotes for interim facilities and terminal works. Seek matched quotes and term sheets, test paid trips, affordability and renewal funding, then compare price and localisation commitments. |
| Which interfaces to prototype first | The [mechanical study](../cities/Baghdad/engineering/mechanical/README.md) screens body, bogie, straight platform and typical span together. The [controls replay](../cities/Baghdad/engineering/controls/README.md) exercises platform-side doors, traction inhibition and section loss. | Obtain wheelset and frame dimensions, check curved-platform sweeps, trial a bogie removal and check bearing seats against ground and erection loads. Instrument the simulated brake handover and reset sequence on a loaded rig. Record mass, load, clearance and test results against the same revision. |
