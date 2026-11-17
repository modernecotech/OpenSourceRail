# v0.7 engineering status

This is the current decision register for the first prototype-production package.
The [architecture](ARCHITECTURE.md) defines the selected reference; the
[release gate](RELEASE-v0.7.md) defines completion. Calculated research results
are evidence for a decision, not permission to manufacture or carry passengers.

## Configuration boundaries

| Application | Identity and purpose | Current decision |
|---|---|---|
| Selected vehicle | Physical candidate `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`; six 17 m passive-wheel comfort cars | Development reference. Installed propulsion and complete vehicle mass remain open. |
| Synthetic 30 km | Requirements `a18e0f20b6ec40e067aff40213b312ae756f7f3389ee5b43059225cf92d05ff4`; [current-source evaluation](design-engine/line30-current-20261117/README.md) `947dd7cbcac7c260da721150912fba47531c96fd3f7a28365c394249608ee869` | Equal-service cost and service control, not an actual alignment. |
| Samawah | [Current-source city evaluation](design-engine/v07-affordable-corridor/README.md) `d69d46f7adccfcaf9d9d799d6c478741e0a3010e2b0a4f20d8d34d119ccf5291` | Distinct 57.873 km planning case. The 5.738 km line-1 gap fails the retained level coasting assumption. Grades are unsurveyed. |
| Baghdad | [148.2 km and 605.65 km concepts](proposals/baghdad-v07/README.md) | Strategic planning only. Route, demand, capacity and installed capital require their own evaluations. |

## Prototype-production decision register

| Assembly or interface | Defined now | Required to issue a controlled prototype package |
|---|---|---|
| Propulsion and braking | [Equal-assumption demonstrator screen](design-engine/v07-demonstrator-propulsion/README.md) compares station-only, a bounded booster and powered-wheel demand on 1.5–2 km synthetic legs. Station-only stalls on the 2 km, 2% uphill case; the booster and powered wheels reach analytically. Assumed friction adhesion 0.05 is below the necessary bound for the 0.6 m/s² independent stop. | Survey the demonstrator profile; define stator/vehicle datums, powered limits, feeder/return, independent brake and protected tow. Measure full-scale moving force/current/heat through repeated duty and faulted stops. Installed drive selection remains open. |
| Representative car | [Prototype planning handoff](design-engine/v07-representative-car/README.md) maps seven research-child structural/running scopes and 71 leaf rows to selected-car interfaces. [Mass reconciliation](design-engine/mass-reconciliation/current/README.md) accounts for 19,221.998 kg/car, of which 10,090.200 kg is residual rather than placed equipment. Child mass and cost are not added to the selected car. | Locate and weigh bogies, service equipment, HVAC, electrical protection, doors, couplings and repair access; establish whole-car CG/inertia and load paths. Control carbody/bogie, aperture/platform, service-connector and six-car interfaces. |
| Removable door | Research child `907da3680bcbd01ffe1223652443e4e34a9f581e201385917a99edf4150bd90a` has 74 part types and 694 pieces/opening. [Interface handoff](design-engine/v07-execution/door-interface-handoff.json) holds all mating datums and installed transforms. | Measure one car opening; specify guide, pulley, belt, stops, retention, seals, obstruction, release, interlock, electrical rating, tool sweep and replacement path. Cycle and fault-test the full assembly and record timed repair/QA. Do not multiply its provisional cost into the selected car. |
| Viaduct span | Separate segmented physical candidate `abcf7e942fd1337c9872869d684ac9a8055ce94bd3e9c35de0dbcbe07f49ac82`: two 10 m segments per 20 m span, 29.59 t bare each and 34.20 t provisional hook load. [Prototype planning handoff](design-engine/v07-segmented-span/README.md) counts 200 beams, 400 lifts, 202 supports and 800 bearings for a synthetic straight 2 km two-track demonstrator, with six erection load-path stages. | Detail and test key, tendons, anchor zones, lifting points, temporary tower and release stages. Fix bearing and rail datums, crane chart/haul route and site-specific pier/footing design. Monitor a jointed span test before assigning accepted cost or structural status. |
| Station module | A [candidate-bound launch/brake module quote schedule](design-engine/v07-demonstrator-propulsion/README.md) lists eight equipment groups and distinct 350/400/450/550 m receiving research envelopes. At 20 m/s, 0.6 m/s² net stopping, an illustrative 1 s reaction and full-train engagement, the optimistic geometric minimum is 457.8 m. The 550 m option leaves 92.2 m unallocated before berth and uncertainty design; inherited brake adhesion still fails the necessary bound. Installed quantities, electrical ratings, mass and prices remain null. | Survey platform, rail and door datums; size independent stopping and protected recovery with latency and uncertainty; obtain supplier force/current/thermal and protection data; establish accessible maintenance removal and civil mounts. No installed propulsion selection follows from this schedule. |
| Manufacturing and lifecycle | The [underframe production draft](design-engine/v07-representative-car/README.md) maps 16 candidate-linked leaf Items to a 565-piece BOM, routing, QA characteristics and repair draft. All Items are disabled; costs, supplier quotes, process hours and QA limits remain null. A verified Samawah planning edit also produced a current-candidate factory draft, without route performance recalculation or ERP admission. | Approve drawings and process/QA limits, obtain supplier prices and measured hours, validate target ERPNext fields and permissions, then run a controlled receipt, installation and repair handback for the same physical child. No synthetic sample item may stand in for candidate hardware. |

The first physical demonstrator is a **1.5–2 km route to be surveyed**, not an
approved site or a shortened Samawah leg. Its alignment, grade, soil, access,
utility and emergency constraints must be recorded before a drive, footing or
construction method is selected. The next useful deliverable is one mated car,
span and station interface package with named measurements and supplier inputs.
