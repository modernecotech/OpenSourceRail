# Civil design exploration implementation and acceptance

The action plan starts from commit `64549d8`; the implementation starts from
`42c8bf8f0f`, after catalogue regeneration. The first executable workbench is
[`engineering/civil_exploration`](../../engineering/civil_exploration/README.md).
The original Word plan is an external planning input, not a model source.

## Executed software workflow

One command freezes candidate and scenario contracts, replays the existing native
reference, verifies analytical benchmarks and compares complete Pi20/Pi25,
hollow-deck, hollow-pier and combined packages. Native outputs include reaction
balance, dead/axle/braking cases, flexible support response, handling overhangs,
modes, moving-force histories and mesh/time refinements. Its quantities preserve
fabricated, transported, suspended and installed mass distinctions.

The first campaign uses 100 m of double track and the retained LM3 three-car
planning axle pattern. Baghdad six-car supplier geometry is not extrapolated.
Foundation dimensions/stiffness, damping and material/steel allowances are
explicit scenario inputs. Supplier costs and accepted railway limits are absent.
These gaps prevent engineering-feasible rankings regardless of numerical passes.

The expanded `civil-study.py programme` command now connects eight geometric
families, material-region matrices, whole-assembly CAD/IFC, actual C3D20R solids,
nonlinear sections/piles/P-delta, cyclic friction, coupled suspension/contact,
thermal/continuity, complete costing interfaces, multi-seed Pareto search,
range sensitivity, safe artifact retrieval, physical-test planning and the
existing structural release gate. The generated C01–C14 audit records executed
software separately from outstanding engineering acceptance.

Existing baseline verification found stale Baghdad proposal evidence and missing
catalogue manifests. The workbench isolates its source-bound civil reference;
it does not reinterpret those unrelated outputs as accepted engineering evidence.

## Work packages and ownership

Roles below are accountable disciplines, not appointed people or acceptance
signatures. Assign named implementers and independent reviewers before accepting
engineering criteria. Software regression results are not engineering acceptance.

| ID | Owner / acceptance reviewer | Current delivery | Remaining acceptance evidence |
|---|---|---|---|
| C01 | Structural lead / independent structural checker | Frozen study, native reference replay, explicit train/ground/maturity gaps | Adopted code editions, approved load combinations and limits, measured inputs |
| C02 | Analysis/CI engineer / separate software reviewer | Strict material/geometry contracts, source/native identities, child reasons and complete ancestor records | Independent contract review and actual material/connection specifications |
| C03 | Structural/CAD lead / specialist checker | Pi, box, conventional I, U, ribbed, UHPC, hybrid and segmental geometry; existing foundation catalogue linked | Supplier-defined reinforcement, joints, fabrication limits and qualified domains |
| C04 | CAD engineer / quantity checker | Disjoint whole-corridor CAD solids, stable IFC4.3 products/net quantities, native element/material regions | Actual bar/tendon geometry and accepted fabrication/installation drawings |
| C05 | Analysis engineer / structural checker | Analytical native shear/support/modal/vehicle checks, fibre tangent, nonlinear reaction balance, orthotropic coupon and friction limit | Measured material/connection/soil datasets and physical applicability validation |
| C06 | Analysis/CI engineer / separate reviewer | Native nodal exchange uses existing parsers; versioned integration-point stress parser; raw mode/time fields and stale-source checks | Accepted project criteria and reviewed output specifications |
| C07 | Structural/geotechnical leads / independent checker | Native Concrete02/steel sections, nonlinear p-y/t-z/q-z piles and second-order columns | Site-calibrated group interaction, cyclic properties, scour/liquefaction and seismic selection |
| C08 | Vehicle/structural/construction leads / checker | Moving forces, coupled vertical suspension/contact, handling supports, thermal eigenstrain, simple/link-slab/continuous models | Supplier train properties, asymmetric/3D interaction and site-specific erection/thermal cases |
| C09 | Manufacturing/cost lead / cost checker | Complete scope bill, material-separated quantities, source-bound rates/charts, transport and discounted maintenance/replacement | Actual quotes, equipment/support proposals, routes, productivity and maintenance intervals |
| C10a | Analysis/CI engineer / software reviewer | Bounded native workers, source snapshots, recorded failures, attempt budgets, resumable search and CI | Independent clean-environment replay and agreed operational compute budgets |
| C10b | Cost/construction leads / checker | Immutable sub-50-MiB multipart archive and safe hash-verified restore; exercised retrieval | Project artifact custody, retention and hosted backend decision if required |
| C11 | Optimisation engineer / structural lead | Multi-seed constrained Pareto evolution, equal-budget random baseline, native shortlist and range/ranking sensitivity | Accepted constraints/costs and candidate-specific independent qualification |
| C12 | Structural/material specialists / independent checker | Actual-section three-mesh solids, orthotropic material matrices, nonlinear shortlist sections, prestress-loss/camber and friction/fatigue diagnostics | Calibrated hybrid bond/contact, anchorage, deterioration and cyclic failure models |
| C13a | Materials/geotechnical leads / test authority | Detailed protocol/measurement/stop-condition templates and source-bound calibration/holdout processing | Named laboratories, source rights, specimens, procurement and reviewed test loads/limits |
| C13b | Test leads / independent engineering reviewer | Physical results remain absent and explicit | Instrumented coupons, joints, piles and representative assemblies; blind validation |
| C14 | Configuration owner / engineering authority | Sealed impact proposal invokes existing structural gate; research qualification cannot be bypassed | Actual independent check, candidate-specific physical evidence and authority acceptance |

## Corrected sequencing

C10a begins alongside C02–C06 rather than waiting for every commercial adapter.
The early demonstration provides geometry, quantities and bounded response
verification. C07–C09 and C10b progressively add calibrated systems, load coverage
and complete pricing. C11 may explore provisional responses, but confirmed
shortlists require applicable C12 models. C13 procurement starts during C01;
validation follows the relevant model and specimen definition.

The 24-week programme remains an indicative software schedule. Per-package effort,
named staffing, benchmark availability, storage and compute costs must be estimated
before committing to the complete option space. Physical validation and supplier
procurement retain separate evidence-dependent schedules.

## Model acceptance policy

Register the observable, units, analytical/test reference, uncertainty, convergence
tolerance, applicable domain and acceptance owner before treating a capability as
qualified. Independent solver agreement is verification; measured tests provide
validation. Native failure, timeout, uncovered physics and a violated requirement
remain distinguishable. Null prices cannot produce a cheapest-design claim.

The current report records research outcomes with engineering feasibility
`unresolved` and physical/operating release `false`. Existing civil evidence,
structural-release and sealed engineering-change gates remain binding for any
future catalogue adoption. Source snapshots and raw solver outputs stay in
`build/engineering/`; intentional compact review artifacts follow the normal
50 MiB-per-file artifact policy.
