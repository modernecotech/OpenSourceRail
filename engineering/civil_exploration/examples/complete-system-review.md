# Complete viaduct system exploration

Baghdad target. Common scope: **300 m, double track**. 731 distinct packages, 779 evaluation attempts, 128 provisional screening passes.

**Actual supplier costs are unknown. No engineering-qualified cheapest design or global optimum is claimed.**
The static load is the retained infrastructure full-train allowance spread over the retained train length. It is not an actual axle pattern or dynamic envelope.

Winner basis: converged native shortlist and provisional deflection screen. Price and productivity scenarios are synthetic assumptions; masses follow canonical material regions and full package quantities.
Material strength/prestress/fatigue capacity remains unresolved. Gross stresses are retained without an invented material-independent acceptance limit.

| Scenario | Objective | Beam / pier / foundation / method | Installed cost USD | Installed mass t | Working days | Largest lift t |
|---|---|---|---:|---:|---:|---:|
| concrete-first | cheapest | U-girder 20 m / lightweight / hollow-tapered / CFA-six / in-situ / link-slab | 1,774,796 | 6,504.4 | 120 | 0.0 |
| concrete-first | lightest | hybrid-shell 20 m / high-performance + GFRP / hollow-prismatic / square-driven-six / precast-full / link-slab | 7,374,804 | 5,499.2 | 154.625 | 43.3 |
| concrete-first | fastest | uhpc-ribbed 20 m / normal / solid-tapered / CFA-six / precast-full / simple-span | 2,259,846 | 7,803.8 | 64.375 | 57.6 |
| lightweight-industrial | cheapest | U-girder 20 m / lightweight / hollow-tapered / CFA-six / in-situ / link-slab | 1,723,577 | 6,504.4 | 120 | 0.0 |
| lightweight-industrial | lightest | hybrid-shell 20 m / high-performance + GFRP / hollow-prismatic / square-driven-six / precast-full / link-slab | 4,034,997 | 5,499.2 | 137.5 | 43.3 |
| lightweight-industrial | fastest | uhpc-ribbed 20 m / normal / solid-tapered / CFA-six / precast-full / simple-span | 2,088,820 | 7,803.8 | 64.375 | 57.6 |
| resource-constrained | cheapest | U-girder 20 m / lightweight / hollow-tapered / CFA-six / in-situ / link-slab | 2,071,624 | 6,504.4 | 119.125 | 0.0 |
| resource-constrained | lightest | hybrid-shell 20 m / high-performance + GFRP / hollow-prismatic / square-driven-six / precast-full / link-slab | 7,977,508 | 5,499.2 | 214.25 | 43.3 |
| resource-constrained | fastest | uhpc-ribbed 20 m / normal / solid-tapered / CFA-six / precast-full / simple-span | 2,466,096 | 7,803.8 | 76.875 | 57.6 |

## Family coverage

| Beam family | Native completed packages | Model / evidence maturity |
|---|---:|---|
| pi | 43 | Research; gross elastic properties, actual supplier details and physical validation open |
| hollow-box | 61 | Research; gross elastic properties, actual supplier details and physical validation open |
| conventional-I | 42 | Research; gross elastic properties, actual supplier details and physical validation open |
| U-girder | 85 | Research; gross elastic properties, actual supplier details and physical validation open |
| ribbed-deck | 42 | Research; gross elastic properties, actual supplier details and physical validation open |
| uhpc-ribbed | 88 | Research; gross elastic properties, actual supplier details and physical validation open |
| hybrid-shell | 75 | Research; gross elastic properties, actual supplier details and physical validation open |
| segmental-box | 131 | Research; gross elastic properties, actual supplier details and physical validation open |
| steel-composite-I | 97 | Research; gross elastic properties, actual supplier details and physical validation open |
| frp-composite-I | 67 | Research; gross elastic properties, actual supplier details and physical validation open |

## Detailed confirmation

24 shortlisted packages; 24 completed converged three-mesh solids and 3D frame checks.
3D models include two separate tracks, flexible transverse hollow caps, finite bearing translations/roll and coupled foundation translation/rotation. Both-track and single-track uniform loading are retained at three deck meshes for both soil scenarios.
Composite connector sensitivity compares noncomposite, partial interaction and strong-connector behaviour; connector values are unmeasured assumptions. These checks do not supply bond failure or cyclic/fire evidence.

## Document work packages and remaining acceptance

| Package | Implemented software / retained output | External acceptance still required |
|---|---|---|
| C01 | source-bound Baghdad planning inputs and explicit qualification blockers | project inputs, applicable domain and responsible independent engineering acceptance |
| C02 | strict candidate inputs, package/candidate IDs, immutable results and modification events | project inputs, applicable domain and responsible independent engineering acceptance |
| C03 | ten beam, six pier, nine foundation options, material compatibility and bounded search | project inputs, applicable domain and responsible independent engineering acceptance |
| C04 | shared disjoint CAD/IFC solids, net material quantities, shipping/lift unit centres | project inputs, applicable domain and responsible independent engineering acceptance |
| C05 | analytical/native component checks, foundation reciprocity/energy and three-level refinement | actual instrumented tests, laboratories, independent reviewer and acceptance |
| C06 | native CalculiX nodal/stress parsers and complete 3D force/displacement fields | project inputs, applicable domain and responsible independent engineering acceptance |
| C07 | native nonlinear component benchmarks and coupled geometry-specific elastic pile groups | project inputs, applicable domain and responsible independent engineering acceptance |
| C08 | uniform planning sensitivity, separate 3D tracks/caps, method/stage schedules and construction units | project inputs, applicable domain and responsible independent engineering acceptance |
| C09 | complete material/plant/labour/overhead/maintenance/replacement bills and three conditional scenarios | project inputs, applicable domain and responsible independent engineering acceptance |
| C10 | bounded seeded runs, checked checkpoints, sealed raw data, multipart archive and verified restore | project inputs, applicable domain and responsible independent engineering acceptance |
| C11 | equal-budget random/evolution search, Pareto sets, scenario reversals and a diverse shortlist | project inputs, applicable domain and responsible independent engineering acceptance |
| C12 | three-mesh actual-section solids, orthotropic materials and connector-slip/torsion diagnostics | project inputs, applicable domain and responsible independent engineering acceptance |
| C13 | candidate-specific instrumented physical-test protocols and existing calibration/holdout workflow | actual instrumented tests, laboratories, independent reviewer and acceptance |
| C14 | sealed change proposal and pointers to the existing controlled change/structural release process | actual instrumented tests, laboratories, independent reviewer and acceptance |

## Open qualification inputs

- **TRAIN-AXLE-POSITIONS** (rolling-stock supplier): six-car supplier drawing with all 24 axle positions — open.
- **TRAIN-LOADED-DISTRIBUTION** (rolling-stock supplier/structural lead): case-specific loaded axle forces and balanced loaded mass — open.
- **TRAIN-SUSPENSION** (rolling-stock supplier): per-axle sprung/unsprung masses, suspension, contact and bogie/articulation relationships — open.
- **TRAIN-OTHER-CASES** (supplier/structural lead): AW3, infrastructure, braking/rescue/maintenance, lateral and dynamic combinations — open.
- **GROUND-CALIBRATION** (geotechnical lead): support-zone boreholes, calibrated axial/lateral/group/settlement parameters and pile tests — open.
- **MATERIAL-AND-TENDONS** (materials/structural lead): actual concrete/composite batches, reinforcement, tendons, anchorage and losses — open.
- **CODES-AND-LIMITS** (engineers of record): adopted Iraqi/project standards, load combinations and accepted limits — open.
- **SURVEY-AND-ERECTION** (survey/construction leads): accepted alignment/support locations, temporary stages, actual rigging/routes and equipment charts — open.
- **QUOTATIONS** (cost/manufacturing owner): Baghdad-local supplier quotations, productivity and maintenance/replacement inputs — open.
- **PHYSICAL-AND-INDEPENDENT** (independent checker/authority): instrumented validation, independent review and existing controlled authority acceptance — open.

## Further model domains

- moving/coupled Baghdad train requires supplier records.
- nonlinear 3D cyclic/seismic and scour/group calibration.
- reinforcement/prestress/joint/contact capacity and stage locking.
- physical fire/durability/fatigue and independent acceptance.
- V-piers/Y-caps: inclined/multiple-leg 3D cyclic and cap-joint qualification; requires-purpose-specific-adapter-and-data.
- ground-improvement-shallow: site treatment trial/calibration and inclusion-platform load-transfer model; requires-purpose-specific-adapter-and-data.
- recycled-primary-members: qualified material fatigue/durability datasets; secondary nonstructural use remains separate; requires-purpose-specific-adapter-and-data.
- haunched-variable-section: supplier section/tendon/diaphragm detailing and stage qualification; requires-purpose-specific-adapter-and-data.

Actual soil, supplier train records, material/connection details, quotations, physical tests and independent acceptance determine whether any shortlisted package is adoptable. Physical and operating release remain false.
