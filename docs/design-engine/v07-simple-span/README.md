# Joint-free 10 m civil prototype option

This is a **quotation and necessary-bound engineering packet**, not an approved bridge or a change to the selected v0.6 railway. It tests one 10 m, simply supported, one-piece box beam per track/span, carrying 1435 mm conventional rail and a 72 km/h research speed cap. Its physical ID, evaluation ID, complete source hashes and detailed 41-section moving-load envelopes are in [plan.json](plan.json). Run `python3 -m engineering.design_search.simple_span_prototype check --output docs/design-engine/v07-simple-span/plan.json` from the repository root to reproduce the packet.

## Explicit load and section

The selected six-car vehicle is the load parent. The powered-bogie research child adds a **provisional 2.4 t/car** equipment allowance. This yields **25.072 t/car normal** and **33.622 t/car crowd control** over four modelled axles per car. The true installed mass, axle reactions and equipment distribution remain open. The 2.0 m wide, 1.4 m deep closed box, concrete material assumptions, 60E1 rail and direct-fastener account come from the existing civil evaluator. Nine provisional strands are sized for the crowd case and retained for the normal evaluation, so both load cases refer to the **same beam component**. Prestress force and rebar rate are model hypotheses, not approved shop details.

| Necessary-bound result, one 10 m beam | Normal | Crowd control |
| --- | ---: | ---: |
| Maximum moving-load longitudinal moment | 0.437 MNm | 0.586 MNm |
| Gross elastic vertical deflection envelope | 0.817 mm | 0.967 mm |
| Maximum gross service compression | 1.831 MPa | 2.174 MPa |
| Counted beam/rail/fastener stock | 31.377 t | 31.377 t |

An independent exact-event moving-load evaluator reproduces the crowd moment. The 41 local gross-stress sections, including release stresses, are in the packet. The preliminary longitudinal screen passes **within this model only**. The gross deflection combines separate moving-load positions conservatively; it is neither a measured dynamic response nor an approved rail/OLE movement allowance. An extreme one-axle/one-rail torsion demand of 76.9 kNm is calculated, but unequal rail loading and section torsional resistance are unresolved. Maximum shear and local wheel/rail, web, anchorage and bearing stresses likewise remain unresolved. Magnetic support is not selected; no magnetic-gap credit or limit is applied.

## Construction and quotation comparison

For a straight 2 km, two-track demonstrator with independent supports per track, this option has **400 one-piece beams and lifts, 402 support/foundation positions, and 1,600 hypothesised bearing units**. It removes the **200 midspan joints and 200 temporary joint-tower placements** of the jointed 20 m comparator, which has 400 lifts, 202 independent supports and 800 bearing units. Shared two-track crossheads, station transitions, switches, curves and actual ground could change these counts. The existing segmented piece's mass and price are **not** carried into this option.

The new beam's provisional bare lifting piece is **29.884 t** and a 25% rigging/hoist allowance gives a **37.356 t hook hypothesis**. At a hypothetical 35 t road payload this implies 400 one-piece trips. A 60 t at 12 m crane chart is only a screening assumption. Each 10 m track span requires one lift and no field midspan joint; each comparator 20 m track span requires two lifts, a joint operation and temporary support. Crew hours, crane moves and bracing remain unpriced and unknown. A carrier must confirm axle loads, turning radius and permits; a lift engineer must confirm certified chart at actual radius, ground bearing, inserts, weather, lateral stability and rigging. The gravity-only interior support reaction is **636 kN**, excluding pier and footing weight. One-metre-thick square footing sensitivities are **2.90 m at 100 kPa**, **1.90 m at 200 kPa**, and **1.52 m at 300 kPa**; they do not select a footing. Actual stratigraphy, settlement, flooding/scour, lateral, braking, uplift, seismic and utility loads remain mandatory site inputs.

The packet provides a fabrication/erection sequence and requests for precast, haulage, crane, foundation, bearing, inspection and proof-load quotations. **Installed and lifecycle prices remain unknown.** A supplier can price a controlled next revision, but cannot quote this as an approved constructed span from the current data alone. Accessibility, protected maintenance/evacuation space and passenger safety remain mandatory; no cost trade has waived them.

## Exact closure inputs

Before native Code_Aster/CalculiX stress analysis or prototype release, provide a controlled 10 m shop model with strand path, rebar, anchor zones, end diaphragms, lift inserts, bearing and rail/OLE coordinates; tested material properties; train lateral/braking and dynamic combinations; bearing stiffness; and site soil/settlement and temporary works. Analyse torsion, shear, cracking, fatigue, prestress transfer, handling, erection stability, support deformation and final rail/OLE tolerances. Proof load the representative span and obtain independent structural and construction review. A native solve without those inputs would produce an attractive but non-decisive field; no such solve was admitted. The packet's status remains **held, physically unaccepted**.
