# Passive wayside accelerator findings

Active direction: passive bogies and reaction fins; all traction equipment stays wayside. Powered-bogie studies are retained comparisons.

| Layout | Sites | Bank length | Active primary extent | Min summed overlap | Worst single-fin overlap | 500 m coverage |
|---|---:|---:|---:|---:|---:|---:|
| original-three-20 | 3 | 20 m | 60 m | 0 m | 0 m | 220.5 m |
| previous-six-20 | 6 | 20 m | 120 m | 9 m | 5.75 m | 500 m |
| front-aligned-five-20 | 5 | 20 m | 100 m | 9 m | 5.75 m | 500 m |
| lean-five-17p5 | 5 | 17.5 m | 87.5 m | 9 m | 4.5 m | 500 m |
| overlap-five-21p5 | 5 | 21.5 m | 107.5 m | 9 m | 6.5 m | 500 m |

These are geometric quantities, not thrust or installed-price reductions. At some positions a single bank must meet the whole train demand. The final active bank in the normal 72 km/h request requires about 66.6 kN and 1.33 MW mechanical; electrical input remains unknown.

## Leading-layout faults

| Disabled site | Geometric uncovered travel | Initial overlap | Departure readiness |
|---:|---:|---|---|
| 1 | 91.375 m | False | hold |
| 2 | 84.25 m | True | requires-qualified-degraded-operation |
| 3 | 84.25 m | True | requires-qualified-degraded-operation |
| 4 | 84.25 m | True | requires-qualified-degraded-operation |
| 5 | 91.375 m | True | requires-qualified-degraded-operation |

## Candidate-bound fixed-bank force contract

The five-bank layout is bound to a separate evidence contract (`3b25670995dd2495bdc555deaf4f79e2486ded7375dcd637359b9847c21033c8`) with 5 installed bank records and 18 demand contexts.

| Bank | Start | Length | Component ID | Force-map ID | Available force | Status |
|---:|---:|---:|---|---|---:|---|
| 1 | 91.5 m | 20 m | unknown | unknown | unknown | held |
| 2 | 191.875 m | 20 m | unknown | unknown | unknown | held |
| 3 | 292.25 m | 20 m | unknown | unknown | unknown | held |
| 4 | 392.625 m | 20 m | unknown | unknown | unknown | held |
| 5 | 493 m | 20 m | unknown | unknown | unknown | held |

Required force in each target-demand context is retained separately from available force; no geometry-derived thrust is admitted. The exact primary/winding, electrical groups, phase handoff, converter limits, heat/cooling duty, receiving/braking, installation quantities, prices and physical correlation are still required. The moving-LIM component study remains a separate 12.5 m/9 m configuration and is not transferred into this five-bank contract.


Failed banks remain installed: no mass, stock or price is removed. A middle contact gap does not prove the train stops there; its motion and safe stopping require a validated force/brake model. An unavailable initial bank prohibits self-launch in the specified berth.

Required next work: one/two-fin nonlinear position/force/current/thermal maps; current-control handoff; train-level fin/hanger/coupler load paths; receiving and independent braking; protection, external rescue and complete installation quotations.

Study identity: `00ccbe0a0ec8037507438d3d5979ca73e9c5eb872eb1138d2d6a8bb119b7dac9`.
