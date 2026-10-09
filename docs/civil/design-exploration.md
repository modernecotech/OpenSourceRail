# Civil design exploration implementation and acceptance

The action plan starts from commit `64549d8`; the implementation starts from
`42c8bf8f0f`, after catalogue regeneration. The first executable workbench is
[`engineering/civil_exploration`](../../engineering/civil_exploration/README.md).
The original Word plan is an external planning input, not a model source.

## First milestone

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
| C02 | Analysis/CI engineer / separate software reviewer | Strict schemas, immutable design IDs, run IDs, source/native hashes | Wider material/connection schema and independent contract review |
| C03 | Structural/CAD lead / specialist checker | Pi controls, hollow deck, stepped hollow pier and bounded compatibility | Conventional supplier girder, hybrid/UHPC and qualified family bounds |
| C04 | CAD engineer / quantity checker | Shared section regions, CAD/quantity mapping, native support/connection topology | Full pier/foundation CAD federation, IFC, reinforcement and tendon geometry |
| C05 | Analysis engineer / structural checker | Analytical shear/support/modal/moving-force fixtures; reference preserved | Concrete, composite, joint and physical benchmark domains |
| C06 | Analysis/CI engineer / separate reviewer | Isolated fail-closed worker, force/stress/mode/history fields, hash verification | Versioned interchange into existing civil evidence parsers and signed criteria |
| C07 | Structural/geotechnical leads / independent checker | Linear system, variable pier sections, finite foundation compliance | Calibrated nonlinear soil/pile response, group effects and pier P-delta |
| C08 | Vehicle/structural/construction leads / checker | Retained axle patterns, synchronous tracks, transient/braking and handling cases | Supplier trains, asymmetric/3D dynamics, thermal/continuity and erection sequences |
| C09 | Manufacturing/cost lead / cost checker | Complete reference quantity scope, distinct masses and explicit quote gaps | Equipment charts, local supplier rates, temporary works, production and lifecycle costs |
| C10a | Analysis/CI engineer / software reviewer | Bounded runner, source snapshots, reports, cache/resume, failure attempts | CI and independent clean-environment replay of campaign evidence |
| C10b | Cost/construction leads / checker | Separate scope remains explicit | Complete staged/commercial adapters and versioned long-term artifact retrieval |
| C11 | Optimisation engineer / structural lead | Deferred; deterministic family comparison precedes search | Applicable C12 models, equal-budget sampling baseline, multi-seed robustness |
| C12 | Structural/material specialists / independent checker | Elastic detailed-response shortlist foundation only | Shape-specific shells/solids, prestress, cracking, joint/contact and nonlinear benchmarks |
| C13a | Materials/geotechnical leads / test authority | Procurement and data needs identified | Engage suppliers/labs and obtain datasets from project start |
| C13b | Test leads / independent engineering reviewer | Physical validation pending | Instrumented coupons, joints, piles and representative assemblies; blind holdouts |
| C14 | Configuration owner / engineering authority | Production promotion blocked; evidence bundle separated | Accepted independent review and existing civil/engineering-change release gates |

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
