# Model-based cost and end-to-end delivery closure

**Implementation status — 1 November 2026.** `engineering/design_search/model_cost.py` prices the coupled railway research bundles, and `engineering/development_baseline/system_cost.py` now adapts the exact selected v0.6 vehicle into a separate candidate-bound system scenario. The selected reference remains the six-car, passive-wheel, station-LIM train. Research alternatives retain their own physical/evaluation/selection identities. Safety, accessibility and engineering qualification are never waived by a cost estimate.

### First executable model-cost milestone

For each executed research bundle, the campaign prices occurrence-level body stock and retained equipment accounts, unknown joints and architecture packages, propulsion primary/conversion/support/cooling and installation, generated civil span quantities, bounded foundations/piers, transport, erection, rail installation, stations and service-battery chargers, utilities/depot, fleet, factory tooling/cells, electricity, operating staff, maintenance, renewals, recovery, reliability and end-of-life decommissioning. It emits low/base/high IQD estimates, cost-line identities, source evidence, a production-cell/tooling plan and construction-duration estimate. Production capacity and civil schedules assume two 8-hour shifts per day. Operations cost low/base cases cover 16/18-hour service with two shifts; the high case models 24-hour operation with three shifts. Electrical service includes 35/35/50 kW-per-car hotel-load assumptions and declared battery charging losses. Seven dated July 2026 Iraqi CSO material/wage records are used where their units match; remaining rates and site/asset quantities are explicit Class C assumptions.

The cost result also carries a candidate-bound provisional manufacturing route for every located nominal gross body-stock occurrence. Each route records the selected process hypothesis, material/form, nominal mass, manufacturing-group and operation identities, low/base/high labor-hour proxies, and the matching factory-gate cost-line ID. Hours use the declared process-hours-per-kg range plus setup-hours-per-stock, then scale by the candidate fleet. The route coverage is one-to-one for located body stock only; inherited unlocated equipment, unknown joints, propulsion, final assembly and civil work remain separately estimated or held. These are Class C costing proxies under the stated two-shift production schedule, not measured cycle times, completed shop routings, equipment validation or released manufacturing instructions. The source MBOM's `labor_h` remains unknown until supported by process evidence.

The research campaign is **model-cost complete for each declared synthetic corridor**, not for a city budget. The selected reference also has a source-bound system estimate across all 14 scopes for a separate 6 km periodic corridor, three stations, 2 km spacing and two physical trackways. Its low/base/high installed CAPEX is IQD 59.16 / 286.49 / 1,721.96 billion; its 30-year whole-life NPV is IQD 123.14 / 672.06 / 5,806.45 billion. The costing allowance is six active plus two reserve trainsets. These are wide coupled Class C scenarios, not confidence intervals, quotes, a city plan or a demonstrated economic advantage. The [source-bound selected system record](current/exports/selected-system-cost.json) keeps the physical vehicle ID separate from the route evaluation and cost scenario identities.

The selected six-car vehicle separately has an estimate for 2,482 geometry occurrences and ten positive residual mass accounts: IQD 1.500 / 6.518 / 29.497 billion low/base/high for factory production, assembly and a 50 km reference delivery. The 10.090 t/car residual remains unlocated and possible overlap is unknown; no overlap credit is applied. The system cost does not add that separate vehicle total: it prices the selected geometry and residual-account rows as fleet units.

The system estimate includes provisional support/cooling and a charger package for every station/direction platform. At 200 kW/car and 35 seconds dwell, the declared normal hotel-load case has +0.074 kWh/car per-cycle estimated margin; the 50 kW/car adverse case has a −0.686 kWh/car shortfall. Battery charge acceptance, solar yield, converter/grid capacity and repeated duty remain unmeasured. City route quantities, geotechnical/site data, supplier prices, complete installed mass, force/thermal maps, physically supported journeys and safety acceptance remain open. Estimates from other candidate bundles do not transfer to the selected reference.

### Provisional factory resource envelope

The selected manufacturing export and immutable factory draft now calculate 27 aggregate resource scenarios: batches of 1/6/12 six-car trains over 60/125/250 working days, each with the cost ledger's low/base/high process-hour case. For this sensitivity only, one process hour is interpreted as one person-hour. At 75% productive utilisation each worker supplies six productive hours in one eight-hour shift; two shifts need two distinct sets of staffed positions. Pooled labour gives an arithmetic capacity bound, while separate process-family staffing shows the effect of keeping those resources apart. Every input package retains its cost-line, source and occurrence links, and delivery hours are excluded.

For one train over 250 working days, the 21,428.373-hour base case requires 7.143 pooled positions per shift, rounded up to eight positions on each of two shifts (16 shift positions before relief). This is a declared staffing scenario. Actual crew skills, relief, workstation/machine capacity, concurrent working, assembly/cure precedence, procurement lead times and dated calendars remain open. The envelope neither supplies measured production labour nor releases a shop routing, staffing roster or factory throughput commitment.

## Why calculated costs are enough for design exploration

A complete *planning scenario* does not require an actual vendor quotation for every manufactured panel, chassis, beam, pier or factory process. Given a dimensioned part, material, production route, quantity and explicitly assumed rates, the platform can calculate a transparent low/base/high engineering estimate and compare alternatives. A third-party quote improves confidence when procurement is imminent; it is not a prerequisite for calculating a provisional design cost.

## Three separate completion levels

OpenSourceRail records completion by scope and keeps three decisions independent:

1. **Simulation complete:** every required calculation in the declared study scope has run, and each input is measured, benchmark-supported, or an explicitly identified bounded assumption. A cost scenario can reach this level without a supplier quote. The record names its scope so a complete cost simulation cannot be mistaken for a complete propulsion journey or vehicle model.
2. **Engineering validated:** the relevant physical models and limits are supported by credible evidence, results meet their supported engineering requirements, and an independent review has accepted the evidence. Provisional assumptions can support exploration but cannot satisfy this level.
3. **Approved for manufacture or operation:** the candidate has passed the separate safety, accessibility, manufacturing or operating requirements for the specific release, with the required independent approvals. Manufacturing and operating approvals remain separately scoped.

For the current coordinated comparison, the research Class C cost scenario is complete for 112/112 evaluated bundles across 14 cost scopes. The selected reference has a separate source-bound vehicle estimate and a selected-candidate 14-scope synthetic-corridor estimate. Both price account allowances without closing installed mass or possible account overlap. Integrated force-driven journeys, site-specific city cost, engineering validation and manufacture/operation approval remain open.

The existing work includes a component/material master (engineering/component_registry), gross/net takeoffs (engineering/sourcing/manufacturing.py), candidate-bound Iraqi material-plus-labour screens with a configurable uplift (engineering/sourcing/fabrication.py), geometric production hypotheses (engineering/railway_progress/production.py), conditional A/B/C manufacturing and lifecycle costs (engineering/reference_cell), and ERPNext/Frappe handoff components (services/integration/osr_integration). **The selected-corridor adapter closes a declared synthetic financial scope; these tools still do not form a site-validated, consistently priced city-delivery ledger.** Integration must preserve scope and evidence distinctions.

There must be three distinct completion flags:
- **Model-cost complete:** every required scope has a quantified bill of quantities, explicit assumptions, bounded scenario costs, scope coverage and no unclassified missing items. Class C scenarios are permitted.
- **Procurement ready:** quantities/specifications have been checked for purchase, supplier or manufacturer offers and logistics/terms are reviewed, and approvals are granted. This is not implied by a model-cost-complete result.
- **Physically/safety accepted:** relevant vehicle, guideway, traction, braking, accessibility, control and site evidence has passed the project's independent engineering/assurance process. No economic model can set this flag.

## Canonical stage-by-stage process

| Stage | Canonical input | Generated output | Next decision / feedback |
|---|---|---|---|
| 1. Define remit | City geography, passenger demand, climate/site assumptions, service/comfort, safety/accessibility, local production | Revision-bound requirements, scenario ranges and hard vs revisable constraints | Reject incomplete/contradictory scope |
| 2. Generate architecture | Requirements, typologies, material and assembly grammar | Separately identified rolling-stock, propulsion, civil, station and production candidates | Explore alternative families, not just dimensions |
| 3. Detail parts | Candidate, material forms, CAD/IFC and interfaces | Occurrence-level EBOM, geometries, installed positions, mass/CG/inertia and unresolved account ledger | Design missing support, HVAC, cable, fastener, joint and access items |
| 4. Evaluate function | Same candidate, loads, motor/brake map, site/environment envelopes | Model-domain/fault results, force/heat/strength/clearance margins and explicit blockers | Revise geometry/material/topology or request a better model/test |
| 5. Plan production | Approved research configuration, part stock/blank and assembly graph | Gross takeoffs, MBOM, cut lists, operations, equipment, tooling, workstations, crews, yield and inspection plans | Revise methods if production time or access is poor |
| 6. Calculate costs | EBOM+MBOM, process routes, reference rates, amortisation and uncertainty | Low/base/high factory-gate, delivered, installed and lifecycle costs, coverage and source classes | Prefer cheaper Pareto options; surface uncertainty |
| 7. Plan the city | Route-specific civil, stations, fleet, depot, factory output, construction methodology | Production capacity, two-shift schedules, cranes, logistics, CAPEX cashflow, OPEX/renewal and passenger service | Recalculate fleet, schedule, plant scale and capital requirements |
| 8. Prepare execution | Reviewed candidate and approved data | ERPNext/Frappe HR Item, BOM, routing, workforce, purchasing, QA and project draft records | Human authorisation before ordering or issuing site work |
| 9. Build, test and operate | Fabricated serial parts, site measurements, commissioning and independent approvals | As-built revisions, inspection/test records, FUXA monitoring, maintenance/repair data | Feed true material usage, hours, failures and costs back into new estimates |

The existing ./osr design railway, ./osr-twin, ./osr-cell and ./osr design progress commands cover parts of stages 2–6. City planning, ERPNext and FUXA are retained but not one commissioned end-to-end execution flow. Stage completion must identify what is executable, estimated, held and independently accepted.

## One cost grammar for every manufactured and installed item

Use a canonical cost record with: candidate/evaluation identity; physical part, occurrence and production batch; quantity and units; material grade/form/source/origin; geometry net and purchase-gross takeoff; scrap/yield; process route and setup/cycle times; crew rates; machine, power, consumable, mould/tooling and QA allocations; packing, transport, lift, installation and rework; currency/date/location; overhead allowance and its base; low/base/high uncertainty; and a link to the resulting line item. Distinguish a finished purchased assembly from raw inputs so that labour is not counted twice.

Proposed calculations, with each term separately stored:

1. **Materials:** sum of gross purchase quantities multiplied by dated or explicitly assumed unit rates. Gross takeoff comes from nesting, dimensional blank, concrete recipe or process yield; it is not necessarily the finished installed mass.
2. **Labour:** sum of setup hours divided by batch quantity, operation hours per item, handling, assembly, inspection and expected rework hours, each multiplied by the corresponding *loaded* hourly rate (or a clearly labelled base-wage proxy).
3. **Equipment/process:** machine hours × machine rate plus electricity, tooling/mould amortisation, maintenance, consumables, factory handling and dedicated QA not already included elsewhere.
4. **Factory-gate:** materials + labour + equipment/process + any explicit overhead/contingency provision. A quick Class C fallback is **(material + direct labour) × 1.20**, clearly named a *partial factory screen*. If equipment/overhead are itemised, the 20% must only apply to the declared non-overlapping base.
5. **Delivered:** factory-gate + packing + transport + insurance/customs where applicable + unloading.
6. **Installed:** delivered + lifts/rigging + site labour + connections + temporary works + equipment testing + interfaces and civil/site preparation. Foundations, utilities and rails are separate scopes where not already in the product BOM.
7. **Lifecycle:** initial installed system + fleet/energy/staff + spares/maintenance/renewals + downtime/reliability + disposal, as a time-dependent scenario with consistent service assumptions and explicit discounting.

Make the default design-stage assumption three cases (low/base/high), including wage and material-rate sensitivity and alternative production volumes. A **20% uplift is a declared scenario, not a universal supplier margin, a warranty or proof that a finished design is affordable**. Scenario results must stay linked to their assumptions.

### Worked route: a composite carbody panel

CAD determines actual area, number of laminate plies, core volume and insert/fastener count. The process generator selects one of hand lay-up, vacuum-assisted infusion, press/tool, or purchased panel with feasible applicable material and workshop bounds; it calculates glass, resin/hardener, core, adhesive, consumables, gross stock, mould life, cure/trim hours, crew, QA and scrap. The cost grammar prices this as a conditional factory-gate range, then transport, positioning, joining, sealing and installed inspection. If stiffness, heat, fire or assembly constraints fail, design-search changes the layup, material, shape, joint or production method and recalculates the **same downstream installed/economic scopes**. The manufacturing cost can be provisional even while physical qualification remains held.

### Worked route: a 20 m precast guideway span

Use the candidate's counted concrete volume, reinforcement, prestress and anchors, rail/fasteners and support interfaces. Generate work instructions for mould preparation, reinforcement/tendon placement, casting, curing, stressing, testing, demoulding, storage, loading, haulage, erection, bearings and rail completion. Calculate crew/equipment hours and plant utilisation. Include piers/foundations, cranage or launcher, traffic management, access and utility interfaces as separate but linked site scopes. Never call the current concrete+rebar+base-wage screen a complete beam, installed span or route-kilometre cost.

### Bought specialist subsystems

For a wheelset, brake actuator, inverter, HVAC, lift, safety controller or cell without a matched quote, use a separately identified benchmark/analogue or bottom-up engineering estimate with bounded mass, quantity, specifications and installation. Label the evidence Class C/B, unknown subassemblies and uncertainty; do not invent compatibility, fatigue life, railway certification or service duty. Procurement can seek quotations later. When a finished-equipment price is selected, suppress duplicated raw manufacturing charges but retain its supports, installation, testing and lifetime maintenance.

## Feed every failure back into design

The coordinator should translate each blocker into an owned action:

- Missing stock/weight -> generate component, allocate approved source account, resolve collision and recompute CG/axle reactions.
- Missing unit price -> compute Class C recipe/benchmark range and request a stronger rate only if it changes Pareto ranking.
- Failed structural or thermal margin -> propose physical shape/grade/layup/joint/support alternatives, not weaker acceptance limits.
- Infeasible station launch -> explore winding length, number of sections, converter duty, train mass and separate alternate propulsion architectures under new candidate identities.
- Excessive beam/site cost -> compare span section, prestressing, foundation, factory throughput, erection method and traffic impact.
- Unbuildable install -> redesign joints, modularity, access and sequence, then regenerate construction/workforce tasks.
- Unsupported physical proof -> retain the numerical result but create a simulation refinement, bench-test or independent review task; do not mark it passed.

Require a bounded number of alternatives and a continuation frontier; archive all evaluations, including failures. Prioritise by expected improvement in whole-life cost and passenger service, feasibility and the value of reducing uncertainty. Only an independently checked selection may advance to the prototype gate.

## Implementation increments and regression gates

| Increment | Integration work | Test for completion |
|---|---|---|
| C1. One cost API | Connect engineering/sourcing/fabrication.py and engineering/reference_cell/manufacturing.py through one current-candidate scope/quantity/evidence record while preserving source-bound output identities | The same panel/span recipe prices identically across the current Workbench, BOM and economic report |
| C2. Complete occurrence mapping | Bind engineering/component_registry and engineering/mass_ledger_audit.py to every MBOM and cost line; handle assemblies/unknown account balances explicitly | Every installed item is counted once; unmatched masses and scopes are named, not zero |
| C3. Rich process routes | Extend engineering/railway_progress/production.py with mould/cure, welding, cutting, transport/erection, labour resource and equipment amortisation | Price a carbody panel, frame, bogie, LIM bank and box/twin/U span with alternate methods |
| C4. Scenario/uncertainty engine | Use dated Iraqi material/wage references where available; add transparent assumed ranges and 10/20/30% sensitivity where applicable | Show low/base/high model-cost completeness even with zero compatible supplier offers |
| C5. Factory/city aggregation | Feed engineering/reference_cell/economics.py with batch rates, factory capacity, civil/site installation, fleet and city scope; prevent double counts | Route CAPEX, annual OPEX, lifecycle and construction calendars reconcile by exact candidate |
| C6. Adaptive feedback | Feed priced method and manufacturing blockers into engineering/design_search campaigns; retain rejected alternatives | Candidate changes recompute geometry, mass, cost, energy, forces and schedule consistently |
| C7. Business bridge | Generate versioned draft Items/BOMs/Routings/Operations/Projects for ERPNext and configured observation interfaces for FUXA | Explicit human approvals; drafts cannot purchase, commission or move trains |
| C8. Physical and safety release | Preserve current tests, candidate identities and independent evidence/approval gates | Class C affordability never implies supplier compatibility, safe operation or manufacture release |

The cost engine and selected-corridor adapter now provide the declared-scope estimates in C4 and a synthetic instance of C5. C1–C3, site-quantity validation and city-route aggregation remain partial. A cost scope can be complete under assumptions while its physical inputs, site basis or purchasing basis stay unvalidated.

Tests should also prove that price-source changes update estimates without inventing new physical parts; material/geometry changes invalidate dependent engineering; date/FX/currency and origin errors cannot silently mix rates; 20% is not applied twice; purchased assembly and fabricated-material charges cannot overlap; and results are comparable only for equal transport capacity, route and lifecycle service.

## Immediate development decision

**Next:** improve the provisional service-energy supply scenario because the adverse 50 kW/car hotel-load case does not recover the declared energy during a 35-second stop. Compare service-battery capacity/charge acceptance, station charging power, solar contribution and an independently powered service supply under the same candidate identity when only assumptions change; a hardware change must create a new physical candidate. In parallel, replace generic residual-equipment price allowances with account-specific component descriptions where source accounts support them, and replace synthetic route/site quantities with candidate-specific planning inputs. Keep residual mass and overlap unresolved until located evidence exists, and preserve all physical, manufacturing, procurement and operating-release gates.
