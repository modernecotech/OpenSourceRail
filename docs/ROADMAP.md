# v0.6 engineering and delivery roadmap

The next milestone is one complete, internally consistent v0.6 research
candidate. It must carry visible assumptions through installed inventory,
engineering checks, manufacturing, civil construction, service and whole-life
costing. Calculated values can complete research scenarios; unsupported physical
performance remains an explicit hold.

## Active work sequence

1. **Reproducible candidate evaluation.** Keep source, tool, candidate, load,
   mesh and resource identities bound to each result. Regenerate current
   publications from their source definitions and preserve failed, interrupted
   and nonconverged executions.
2. **Complete installed vehicle inventory.** Place every major item or identify
   a bounded equipment reserve. Record geometry, material, mass, interfaces,
   installation method, cost basis, confidence, centre of gravity and inertia.
   Reconcile inherited allowances without double-counting replacement geometry.
3. **Establish physical feasibility.** Refine load paths, joints, strength,
   stability, fatigue, wheel/rail dynamics, braking, service energy, thermal
   performance and station-motor force maps. Run a same-candidate protected
   launch, coast, arrival and fault-stop journey.
4. **Complete production and construction planning.** Assign every part a
   provisional manufacturing or purchasing route. Price factory work, delivery,
   installation, foundations, rail, erection and QA using dated sources or
   explicit low/base/high assumptions.
5. **Compare equal service and lifecycle cost.** Carry the same passenger
   service through fleet size, stations, propulsion, factories, civil works,
   operating hours, energy, staffing, maintenance and renewals. Preserve
   uncertainty and Pareto alternatives.
6. **Prepare evidence and deployment handoffs.** Generate candidate-linked
   business, workforce, procurement, production and supervision records as
   drafts. Build representative prototypes and correlate measurements with the
   models before engineering review or release.

The coordinated work starts with
[`./osr design railway`](design-engine/coupled-railway/README.md). The
[model-based cost and delivery plan](design-engine/model-based-cost-and-delivery.md)
describes the provisional costing and production pipeline. The
[current dossier](design-engine/current/README.md) records present results and
open evidence tasks.

## Current shift and costing assumptions

The current cost scenario uses two 8-hour shifts per production day and two
8-hour civil shifts. Operating cost uses two shifts for 16/18-hour service and
three shifts for the 24-hour case. Shift premiums, utilization, relief staffing
and wage uncertainty are explicit assumptions; they do not establish a local
roster, construction calendar or approved operating plan.

Internal estimates can compare designs before quotations are available. Every
line must identify its quantity, rate source or engineering assumption, scope,
uncertainty and exclusions. Factory cost, delivered cost, installed cost and
whole-life cost remain distinct totals.

## Physical and release gates

The following remain open until the applicable models and evidence close them:

| Area | Required evidence |
|---|---|
| Vehicle | Located equipment, complete installed mass/CG/inertia, qualified load paths, joints and running gear |
| Station propulsion | Available force and duty over position, speed, current, frequency, air gap and temperature; losses and fault response |
| Braking and service | Measured or validated brake/WSP curves, adverse stops, HVAC and essential-power endurance |
| Protected journey | Same-candidate launch, coast, receiving, continuous protection, recovery and fault stops |
| Civil and construction | Route-specific ground/site inputs, moving loads, foundations, erection, access and inspection |
| Economics | Equal-service factory-to-installed and lifecycle ranges with operating shifts, maintenance and renewal scope |
| Prototype and operation | Controlled drawings, processes, tests, independent review and applicable safety/accessibility acceptance |

Software completion, numerical convergence and a favorable estimate do not
substitute for these physical and independent acceptance requirements.
