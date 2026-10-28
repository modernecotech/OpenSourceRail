# Sourced reference-cell design generation

OpenSourceRail links local design, manufacture, construction, operation and repair through open component knowledge and immutable revisions. This separate current research layer preserves the selected wheel/LIM reference, the six earlier twin regressions and all historical source-bound evidence.

`./osr-cell` connects a manufactured-material master, part definitions, individually located occurrences, five equipped 17 m proposals, a typed architecture registry, coupled simulation admission, two-station civil quantities, manufacturing and whole-life cost interfaces, disabled delivery drafts and an interactive engineering Workbench. It does not issue physical, manufacturing or operating release.

## Run and inspect

```bash
./osr design railway plan
./osr-cell plan
./osr-cell run --state build/reference-cell --max-cases 2
./osr-cell run --state build/reference-cell --max-cases 10
./osr-cell verify build/reference-cell
./osr-cell verify build/reference-cell --require-complete  # exit 3 while evidence/design gaps remain
./osr-cell publish build/reference-cell
./osr-cell verify-publication
./osr-cell workbench --state build/reference-cell
./osr-cell cad --vehicle V1 --output build/reference-cell-cad/V1
```

Runs retain exact sources and completed/pending requests under invocation budgets and a single-coordinator lock. Cached reports undergo semantic replay; a receipt hash alone cannot invent a successful design. The Workbench has design, mass/cost, simulation, closure and manufacturing/construction views. All HTTP mutations are refused and validated response snapshots remain immutable during review. Its geography route explains the current v0.6 evaluation hold and does not send users into historical engineering as if it were current.

## Component and material master

[The registry](../../../engineering/component_registry/README.md) separates part definitions, commercial/evaluation revisions and physical occurrences. Physical material grade/form/layup changes revise hardware; revised property estimates invalidate analysis and costs without inventing a new physical geometry. Rigid poses, net volumes, exact uniform primitive inertia, mass intervals, assemblies, process routes, provenance and maintenance/removal envelopes are explicit. Purchased envelopes have independent mass bounds and unknown material/internals, not fictitious dense-solid weights.

The initial catalogue covers glass-fibre laminate, PET core, aluminium extrusion/sheet, structural and fastening steel, copper, glazing/polycarbonate, concrete, elastomer and adhesive. Retrieved manufacturer documents have actual byte hashes. Failed source retrievals and research ranges remain identified; catalogue typicals never become approved laminate, joint, fire or fatigue allowables or delivered-lot evidence.

## Five equipped research vehicles

| Vehicle | Declared load path |
|---|---|
| V1 | GFRP semi-monocoque with metallic hardpoints |
| V2 | Participating sandwich roof/floor monocoque |
| V3 | Aluminium extrusion frame with modular GFRP cladding |
| V4 | Aluminium stressed skin |
| V5 | Aluminium underframe and integrated GFRP cabin |

Each proposal carries the same six-car comfort requirements: 44 fixed seats and two wheelchair places/car, two door sets on one side, passive wheel bogies and segmented passive secondaries, essential/service power, HVAC, solar, independent brakes and control hardware. Shell cassettes, seams, hardpoints, axles/wheels/discs, seals, ducts, cable segments, retention and separate fastener pieces are located. Couplers/gangways bridge the actual half-metre car gaps. Finite swept-envelope checks report potential interference; they do not establish continuous clearance or safe accessibility.

Five fully categorised proposals are not five qualified production vehicles. Holes/copes, detailed supplier internals, route fitup, laminate schedules, validated joints, delivered masses, approved processes and physical support still remain necessary. The dashboard labels occurrence coverage as a count ratio—many small fasteners can dominate it—and separately reports calculated kilograms, declared mass bounds, quote coverage and validation coverage.

## Same-candidate railway and architecture changes

The vehicle registry frame runs from the trailing first-car end to the leading nose at 104.5 m. A declared transform places that nose at route position zero. Actual 24 axle locations and 18 secondary-segment poses feed new canonical cell bundles. These use the generated vehicle mass bounds, actual wheel/disc inertias and new brake/motor/support identities, not the old GFRP train's equipment accounts. Bearing/seal rotation and unknown hardware remain unresolved.

Cell identity includes generated civil/station geometry, motor layout, formation and the body physical definition; changes to cost or an evaluator do not silently change the hardware ID. The architecture registry permits new typed body, running-gear, propulsion, guideway, station and manufacturing definitions. Five/six/ten short-bank variants have owned geometry adapters; longer winding, cable and onboard recovery alternatives remain registered with explicit unsupported hardware/evaluator tasks. No alternative silently replaces the selected reference or inherits a force map.

## Physics and physical tests

The coupled method integrates position/speed, current and voltage limits, electromagnetic loss/RC heat, fade-dependent independent brakes, service/HVAC battery energy and heat, per-axle load transfer, fault events and occupancy. Production admission reuses the authenticated/replayed map gate and additionally requires exact brake/auxiliary/reaction/protection model evidence. Nominal, grade/wind, temperature, bank loss, power loss, emergency braking, low adhesion and disabled/rescue cases share the same physical candidate. A failed-bank map is separately bound; nominal thrust is never divided or multiplied to invent fault performance.

Synthetic equation controls have a separate test-only entry point. An FMI exchange manifest checks model/port/unit/source interfaces; no real FMU execution or validation is claimed without the actual models and tool execution. Existing GoA4/Rust protection remains research software; real sensing, brake correlation, HIL and independent safety review remain mandatory.

The new resource-bounded moving-field derivative preserves the previous physical equations and limits while allowing the same coarse/fine 0.128 s requests to finish. These are component-method studies on their own original rewound candidate. They are not evidence for the new vehicles' segmented fins. [Executed validation](validation.md) records completed runs, disagreement, residuals and the remaining model/physical tasks.

## Civil, manufacturing, commercial and lifecycle scope

Box/twin/U civil hypotheses generate located beam, prestressing/rebar, fastening, bearing, pier/headstock/footing and two-platform stock plus factory/transport/erection records. Actual primary teeth/coils/backiron keep their finite longitudinal extents and bank locations; reactions conserve known weight rather than averaging motors over the corridor. A piecewise-quadratic moving-point-load calculation finds extrema within its declared quasi-static axle/load hypothesis. The span/support reaction tables cover guideway and primary stock; the counted station-platform mass still needs its own defined load path and supports. Rail solids remain equivalent quantity/height envelopes, not an accepted railhead/baseplate interface. Platform placement follows the actual proposed floor and door side, with a declared unqualified boarding gap. This does not qualify prestress losses, piers, ground, lateral/seismic behavior, stations, lifts, drainage, emergency access, crane/rigging or site erection.

Manufacturing exports separate net/gross quantities, yield hypotheses, routings, operations, tooling, inspection, transport and installation. A/B/C costs retain source, date, currency, location and quantity scope. Finished-part quotations suppress duplicated fabrication; purchased/material quotes do not erase installation. Class-A components mixed with class-C labour remain a mixed estimate, not a firm class-A assembly. The shipped class-C sensitivity inputs are explicit illustrative assumptions, not market quotations, installed prices or proof of affordability.

The lifecycle evaluator handles twelve scopes, cashflow years, intervals, discounting, overlapping charges and equal service/fleet/risk comparisons. It requires an explicit scope/calendar and complete service context for a complete conditional NPV. Missing fleet, energy, reliability, quotes or installation records keep whole-life cost and the integrated winner open.

[The integration bridge](../../../services/integration/osr_integration/reference_cell.py) produces candidate/revision-linked Item/BOM/route/RFQ drafts and construction handovers; it does not submit work orders, change released orders, activate assets or commission FUXA equipment. Existing ERPNext/Frappe HR, supervision, manufacturing and operating software retain their original boundaries.

## Completion boundary

The implementation programme's software interfaces can run here. Physical prototype construction/testing, authenticated supplier and site records, independent safety/manufacturing reviews, commissioning and an operating pilot cannot be represented as completed by software. The ten physical protocols, structural/joint qualification, usable force map, complete protected journey and priced whole-life comparison remain explicit gates.
