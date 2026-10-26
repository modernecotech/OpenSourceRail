# v0.6 engineering and prototype roadmap

OpenSourceRail v0.6 develops a station-powered, wheel-supported comfort train. [The selector](../engineering/development-baseline.toml) binds one physical candidate across the [current dossier](design-engine/current/README.md), Workbench, reader and delivery drafts. Six 17 m cars retain 44 seats plus two wheelchair places/car, zero planned standing, one-sided doors and station-led GoA4. Conventional wheel support replaces magnetic levitation; station-only propulsion remains the main new feasibility question.

## Reference sprint

1. Preserve [v0.5 evidence](archives/v0.5-maglev/README.md) and identify the wheel/LIM candidate independently. Retain unchanged component identities and declare every changed interface.
2. Recalculate the equipped 17 m car: passive bogies, concentrated support load paths, passive motor secondary, service battery, brakes, wiring, HVAC and roof. Separate counted material, supplier references and unlocated allocations. Complete installed mass, CG and inertia require closure.
3. Compare box, twin-beam and U-beam concrete guideways under actual axle moving loads. Include rail/gauge fastenings, lateral and torsional loads, prestress, piers, foundations, containment, drainage, walkways, transport and erection.
4. Establish a practical station LIM: full moving force/current/frequency/gap/temperature maps, unwanted normal forces, secondary/stator heat, voltage and switching. Compare single-sided LIM and LSM openly; never substitute prescribed acceleration for available thrust.
5. Couple the same train, motor and independent brake models over 1.5 km, 2 km and the longest retained city gap. Save empty, normal, crowd and adverse cases, including failed arrival, wet rail, power/communications loss, occupied berth and off-zone recovery.
6. Retain existing onboard ATP, interlocking, OCC, TCMS and station-led GoA4 architecture. Qualify physical brake profiles, localisation, integrity, timing and communications; execute fault injection and the existing formal assurance programme. New software predicates do not release a railway.
7. Compare whole-life costs against v0.5 and a station-launch v0.4 derivative at equal route, passenger service and reliability. Supplier prices, installation, maintenance, peak supply and renewal costs remain unknown until supported.

## Executed native follow-up

The [bounded campaign](design-engine/v06-physical-closure/README.md) adds 18 actual current-excited GetDP motor cases, 24 reduced Chrono braking runs, body connectivity checks and native floor fit-up. Counted wheel rotational inertia now feeds the service requirements. The tested full station primary fails its force and linear-steel domain screens. Independent verification rejected invalid body interfaces; frame/joint qualification remains open. None of these executions grants a physical journey or operating release.

Next, redesign the primary for force, steel cross-section, practical gaps and repeated heat together; obtain actual brake/adhesion/WSP curves; and resolve body-joint load paths using independently benchmarked models. Keep service alternatives explicit and compare whole-system quantities before changing the default.

## Failure-driven campaign

The [v0.6 campaign](design-engine/v06-optimisation/README.md) connects the existing immutable/restartable search to generated joined bodies, station LIMs, brakes, actual candidate mass/rotor energy, civil loads and known-stock research twins. Failures now produce physical revisions or bounded numerical/evidence tasks. The campaign budget limits execution; it does not close an unresolved requirement or promote a research winner to an operating design.

Next extend validated physical families and full position/current/temperature motor maps, correlate structural joints and braking with hardware, and execute the same-candidate protected journey. Preserve competing cost/quantity alternatives and retain every failed or interrupted trial.

The [expanded design space](design-engine/v06-design-space/README.md) generates supplier-bound foam/honeycomb, aluminium/GFRP/hybrid, joining and motor alternatives. Necessary bounds reject the retained PVC core at the 80°C research condition; a PET revision preserves ancestry. New directional shear and sandwich-bending method fixtures pass, while new motor samples still fail thrust and material-domain screens. Resolve the diagnosed clamp rotational-restraint deficiency before ranking full-body material substitutions. Corrugated panels and hollow double-skin extrusions remain explicit geometry/data/model tasks.

## Release gates

The [umbrella architecture search](design-engine/v06-architecture/README.md) now runs above component campaigns. Its 509 analytical cases cover seven propulsion families, four/six/eight-car formations, three speed/spacing requirements, powered-track/recovery arrangements and alternative precast sections. It separates mandatory requirements, preferences and revisable hypotheses. Quantity comparisons and explicit unpriced cost expressions do not select an economic winner; installed mass, protected service and native force maps remain holds.

The joint model has six-axis, energy, reciprocity and modal checks with three-dimensional refinement. Its previous 28.018 mm normal displacement exceeds a provisional 25.6 mm comparison; that comparison is advisory in the new policy. Its ideal bond/section transfer needs local strength, slip, fatigue and measurement validation. A generic nonlinear magnetic circuit passes independent field/coenergy method checks; supplier-specific moving LIM, losses and repeated thermal duty remain open. Scheduled native CI repeats bounded method fixtures.

The [function-first adaptive search](design-engine/v06-adaptive-design/README.md) registers 102 extensible variables across 14 domains and distinguishes supported obligations from preferences, design assumptions and numerical domains. Continuous section redistribution now has native normal/fine/crowd executions: the 600×5 mm sill option saves about 48 kg/car versus the prior jointed body and predicts 19.793 mm normal displacement. Do not stop at provisional targets or select by bending alone: continue the frontier through local stability/strength, joining, functional clearances, manufacturing and coupled operating consequences; develop missing material/topology evaluators as active tasks.

Next execute the [M1/M2/M3 programme](design-engine/v06-architecture/prototype-program.json): measured component/joint/brake correlation, a protected passive-carriage launch/coast/stop demonstrator, then an integrated full-sized pilot with recovery. Plans and simulations do not count as completed physical milestones. Reusable native adapters, installed equipment geometry and same-candidate coupled journeys are required before full-system selection.

| Gate | Required result |
|---|---|
| Installed vehicle | Counted, located equipment and complete mass/CG/inertia; qualified body and bogie load paths |
| Wheel/rail dynamics | Ride, hunting, curves, profiles, suspension, axle loads and containment |
| Station drive | Independently validated thrust and duty, practical clearances, switching and fault response |
| Independent stopping | Wet/hot brake/WSP performance, gradients, parking, channel failures and thermal reserve |
| Passenger services | Delivered HVAC at 50°C, hot roof strength, cooled service battery and missed-charge/emergency endurance |
| Protected journey | Same-candidate launch, coast, receive and safe fault stop with continuous ATP |
| Civil and construction | Complete moving loads, prestress/fatigue, site foundations, transport, lifting and inspection |
| Rescue/evacuation | Real off-zone towing, protected access, emergency communication and high-viaduct evacuation |
| Economics | Same-service installed CAPEX, energy, availability, maintenance and renewals |
| Prototype release | Reviewed drawings, processes, tolerances, supplier evidence and instrumented test plan |

## Cities and publication

The 266 city geographies, station locations and underlying city details remain starting inputs. Numerical catalogue-wide regeneration is held until reference propulsion, braking, route and economic evidence permits it. Terrain, grades, climate, demand, transfer access and prices need city-specific assessment. No old fleet or financing number is relabelled v0.6.

v0.6 is selected for research because conventional wheel support removes the unresolved magnetic suspension and its continuous facing system. It may increase vehicle mass; station-only LIM, high platforms and recovery introduce their own costs. Lower whole-life cost is an explicit open decision, not a condition silently assumed passed.

[Current readiness](design-engine/current/summary.json) · [Project introduction](../README.md) · [README coverage](design-engine/current/readme-coverage.md).
